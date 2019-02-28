import json
import spacy
import re
import itertools as it
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from joblib import Parallel, delayed
from tqdm import tqdm
from collections import Counter
from database import articles_with_kw_in_title


def remove_html_tags(text):
    return re.sub(r'(<.*?>)', ' ', text)


def remove_line_returns(text):
    return text.replace('\n', ' ')


def filter_doc(doc):
    for token in doc:
        if token.is_stop:
            continue
        elif token.pos_ not in ['NOUN', 'ADV', 'ADJ', 'VERB']:
            continue
        yield token.lemma_


def process_one_doc(article):
    nlp = spacy.load('en', disable=['parser', 'ner'])
    text = article['text']
    text = remove_html_tags(text)
    text = remove_line_returns(text)
    doc = nlp(text)
    processed = list(filter_doc(doc))
    return processed

def process_one_sentence(article):
    nlp = spacy.load('en', disable=['parser', 'ner'])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    text = article['text']
    text = remove_html_tags(text)
    text = remove_line_returns(text)
    doc = nlp(text)
    for sentence in doc.sents:
        yield list(filter_doc(sentence))


def index():
    articles_ethics = list(articles_with_kw_in_title('ethics'))
    articles_moral = list(articles_with_kw_in_title('moral'))
    articles_morality = list(articles_with_kw_in_title('morality'))
    articles_normative = list(articles_with_kw_in_title('normative'))

    articles = articles_ethics + articles_moral + articles_morality + articles_normative

    processed = Parallel(
        n_jobs=4,
        prefer='processes')(delayed(process_one)(article)
                            for article in tqdm(articles, leave=False))
    processed = [x for y in processed for x in y]

    counter = Counter(processed)
    counts = counter.items()
    counts = sorted(counts, key=lambda x: x[1], reverse=True)
    labels, values = zip(*counts[:10])

    plt.bar(labels, values)
    plt.show()


def cooc_one(article, window_size):
    pairs = []
    for i in range(len(article)):
        current_word = article[i]
        inf = max(0, i - window_size)
        sup = min(len(article), i + window_size)
        window = article[inf:sup + 1]
        for neighbor in window:
            if neighbor != current_word:
                pair = tuple(sorted((current_word, neighbor)))
                pairs.append(pair)

    count = Counter(pairs)
    for key in count:
        count[key] //= 2
    return count


article = articles_with_kw_in_title('ethics')[0]
x = process_one_sentence(article)
a = map(lambda x: cooc_one(x, 2), x)
c = sum(a, Counter())
print(c.most_common(5))

