import logging
import re
import json
import moment
import pprint
import urllib
import unidecode
from bs4 import BeautifulSoup
from tqdm import tqdm
from joblib import Parallel, delayed
from utils import Meta, get, eprint
from database import insert_articles

logger = logging.getLogger('scrapper-sep')
fh = logging.FileHandler('scrapper-sep.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_keyword(keyword, page=1):
    url = 'https://plato.stanford.edu/search/search?page={}&query={}&prepend=None'.format(
        page, keyword)
    return get(url)


def get_page_urls(keyword_res, keyword):
    urls = keyword_res.select('.result_url')
    titles = keyword_res.select('.result_title > a')

    if urls:
        urls = [url.find('a').get('href') for title, url in zip(titles, urls) if keyword in (' ' + title.get_text().lower() + ' ')]
    return urls


def get_pages_range(keyword):
    res = get_keyword(keyword, 1)
    total = res.select_one('.search_total').get_text()
    res_per_page, n_res = re.findall(r'\b([0-9]*) of \b([0-9]*)\b', total)[0]
    res_per_page, n_res = int(res_per_page), int(n_res)
    n_pages = n_res // res_per_page + 1
    return range(1, n_pages + 1)

def get_all_pages(keyword, i):
    return get_keyword(keyword, i)


def get_total_website_urls():
    url = 'https://plato.stanford.edu/published.html'
    content = get(url).select('#content>ul>li>a')
    urls = [urllib.parse.urljoin(url, a.get('href')) for a in content]
    return urls

def process_article(url):
    try:
        article = get(url)
        infos = article.select_one('a[href*=archinfo]').get('href')
        infos = get(infos).stap()
        return str(article), str(infos), url
    except Exception as err:
        print('ERR - get article/infos')
        logger.error(('get article/infos', err, url))
        exit()
        return None

def get_meta(arg):
    article, infos, url = arg
    article, infos = BeautifulSoup(article, 'html.parser'), BeautifulSoup(infos, 'html.parser')

    bibtex = infos.select_one('pre').get_text()
    title = re.findall(r'\ttitle.*\{(.*?)\}', bibtex)[0]
    journal = re.findall(r'\tbooktitle.*\{(.*?)\}', bibtex)[0]
    authors = re.findall(r'\t(author.*?)\n',
                         bibtex)[0].replace(',', '').replace('{', '').replace(
                             '}', ' ')
    authors = unidecode.unidecode(authors)
    authors = re.findall(r'(\b[A-Z].*?\s)', authors)
    authors = [' '.join([b.strip() for b in a]) for a in divide_chunks(authors, 2)]


    try:
        date = re.findall(r'published\son.*?\s(.{3}?)[ ]{1,3}([0-9]*), ([0-9]*)', str(infos))[0]
        date = moment.date(' '.join(date)).date
    except Exception as err:
        print('ERR - get date')
        logger.error(('get date', err, url))
        exit()

    text = str(article.select_one('#aueditable'))

    try:
        related_entries = article.select_one('#related-entries').select('a')
        related_entries = [r.get_text() for r in related_entries]
    except Exception:
        related_entries = []

    meta = Meta(
        main_field='Philosophy',
        journal=journal,
        title=title,
        authors=authors,
        date=date,
        text=text,
        codes=[],
        related_entries=related_entries,
        pdf_link=None,
        website_link=url,
        login_required=False,
    )
    return meta._asdict()


urls = get_total_website_urls()[:5]

#all_pages = Parallel(n_jobs=16, prefer='threads')(delayed(get_all_pages)(KEYWORD, i) for i in tqdm(pages_range, leave=False))
#urls = Parallel(n_jobs=1, prefer='processes')(delayed(get_page_urls)(page, KEYWORD) for page in tqdm(all_pages, leave=False))
#urls = [url for x in urls for url in x]

articles = Parallel(n_jobs=64, prefer='threads')(delayed(process_article)(url) for url in tqdm(urls, leave=False))
articles = [a for a in articles if a is not None]
metas = Parallel(n_jobs=4, prefer='processes')(delayed(get_meta)(article) for article in tqdm(articles, leave=False))

insert_articles(metas)
