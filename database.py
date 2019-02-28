from pymongo import MongoClient

client = MongoClient('localhost', username='root', password='my-secret-pw')

db = client['normative-ai']

article = db['article']

#a = article.find_one()
#print(a)


def insert_articles(articles):
    article.insert_many(articles)


def drop_articles():
    article.drop()


def articles_with_kw_in_title(kw):
    regex = r'(?i){}'.format(kw)
    print(regex)
    cursor = article.find({'title': {'$regex': regex}})
    return cursor

#test = articles_with_kw_in_title('religion')
#print(test.count())

#for t in test:
#    print(t)
