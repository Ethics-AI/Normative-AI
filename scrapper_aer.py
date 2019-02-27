import json
import pprint
import urllib
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

pp = pprint.PrettyPrinter(indent=4)

YEARS_URL = 'https://www.aeaweb.org/journals/aer/issues'


def get(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    return soup


def ym_section_gen():
    articles = get(YEARS_URL).find_all('article')
    for article in articles:
        yield article


def ym_list_gen(section):
    links = section.find_all('a')
    for link in links:
        month, year = link.get_text().split()[:2]
        if year != '2003' or month != 'June':
            continue
        print(year, month)
        a = link.get('href')
        ym_list_path = urllib.parse.urljoin(YEARS_URL, a)
        ym_list = get(ym_list_path)
        ym_articles = ym_list.find_all('article')
        for ym_article in ym_articles:
            try:
                b = ym_article.find('h3')
                if b and 'Front Matter' in b.get_text():
                    continue
                article_path = ym_article.find('a').get('href')
                article_main_path = urllib.parse.urljoin(
                    ym_list_path, article_path)
                article_main = get(article_main_path)
                yield article_main, article_main_path, month, year
            except Exception as err:
                print(err, ym_list_path)


def article_gen(article_main, path, month, year):
    meta = {}
    try:
        codes = article_main.select('.jel-codes')[0]
        codes = codes.select('li strong')
        codes = [c.text for c in codes]
    except Exception:
        codes = []

    download = article_main.select('.download')[0]
    pdf_link = download.find('a').get('href')
    pdf_link = urllib.parse.urljoin(path, pdf_link)

    login_required = 'Complimentary' not in download.text

    title = article_main.select('.title')[0].text

    authors = [
        a.text.strip() for a in article_main.select('.attribution li.author')
    ]

    meta['title'] = title
    meta['authors'] = authors
    meta['year'] = year
    meta['month'] = month
    meta['codes'] = codes
    meta['pdf_link'] = pdf_link
    meta['login_required'] = login_required

    return meta


def full_pipe():
    for section in ym_section_gen():
        for article_main, path, month, year in ym_list_gen(section):
            try:
                article = article_gen(article_main, path, month, year)
                yield article
            except Exception as err:
                print(err)


p = full_pipe()

res = list(tqdm(p))
exit()

with open('tree.json', 'w') as outfile:
    json.dump(res, outfile)