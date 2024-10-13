from flask_login import UserMixin
from pymongo import MongoClient
import pymongo
import pymongo.mongo_client
import os
from bson.objectid import ObjectId
import database


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])   # MongoDB ObjectId converted to string
        self.username = user_data['Username']
        self.password = user_data['Password']  # Hashed password
        self.name =   '%s %s' % (user_data['FirstName'] , user_data['LastName']) #user_data.get('name', 'Default')
        self.active = True   #Active status (default True)

    @staticmethod
    def find_by_username(username):
        user_data = database.RECORDS.find_one({'Username': username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_id(user_id):
        user_data = database.RECORDS.find_one({'_id': ObjectId(user_id)})
        print(f'In find_by_user, userdata = {user_data}')
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
        print(f'In user, id is {id}')
        return User.find_by_id(id)