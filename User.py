from flask_login import UserMixin
from pymongo import MongoClient
import pymongo
import pymongo.mongo_client
import os
from bson.objectid import ObjectId



client = pymongo.MongoClient('mongodb://%s:%s@database:27017/PoolRankings' % (os.getenv('MONGO_USER'), os.getenv('MONGO_PASSWORD')))
db = client[os.getenv('MONGO_DB')]

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])   # MongoDB ObjectId converted to string
        self.username = user_data['Username']
        self.password = user_data['Password']  # Hashed password
        self.name =   '%s %s' % (user_data['FirstName'] , user_data['LastName']) #user_data.get('name', 'Default')
        self.active = True   #Active status (default True)

    @staticmethod
    def find_by_username(username):
        user_data = db.RECORDS.find_one({'Username': username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_id(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    def get_id(self):
        """Flask-Login needs a method that returns a unique identifier for the user"""
        return self.id  # MongoDB ObjectId as a string

    @property
    def is_active(self):
        """Return whether the user is active or not"""
        return self.active

    @staticmethod
    def get(id:str):
        return User.find_by_id(id)