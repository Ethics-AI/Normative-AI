import json
import spacy
import re
from database import articles_with_kw_in_title

nlp = spacy.load('en')

doc = 'eating this duck'
doc = nlp(doc)

for token in doc:
    print(token, token.lemma, token.lemma_, token.pos_)

nlp = spacy.load('en')


text = articles_with_kw_in_title('ethics')[0]['text']
text = re.sub(r'(<.*?>)', ' ', text)
text = re.sub(r'(<.*?>)', ' ', text)
text = text.replace('\n', ' ')[:300]

doc = nlp(text)


for token in doc[:300]:
    print(token, token.lemma_, token.pos_)

