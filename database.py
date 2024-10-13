import urllib
import pymongo
import pymongo.mongo_client
import os

user =  urllib.parse.quote_plus(os.getenv('MONGO_USER'))
password =  urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))

client = pymongo.MongoClient('mongodb://%s:%s@database:27017/PoolRankings' % (user, password))
db = client[os.getenv('MONGO_DB')]

RECORDS = db.RECORDS
MATCHES = db.MATCHES

STARTING_RATING = 500
K = 32
D = 400