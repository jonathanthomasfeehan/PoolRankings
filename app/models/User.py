from flask_login import UserMixin
import app.database as database


class User(UserMixin):
    def __init__(self, user_data):
        self.id = (user_data['id'])  
        self.username = user_data['Username']
        self.password = user_data['Password']  # Hashed password
        self.name =   '%s %s' % (user_data['FirstName'] , user_data['LastName']) #user_data.get('name', 'Default')
        self.displayUsername = user_data['DisplayUsername'] #user_data.get('display_username', 'Default')
        self.active = True   #Active status (default True)

    @staticmethod
    def find_by_username(username):
        user_data = database.get_user_by_username(username)
        print(f"User data: {user_data}")
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_id(user_id):
        """Find a user by their ID"""
        user_data = database.database_get(database.USERS, user_id)
        if user_data:
            return User(user_data)
        return None

    def get_id(self):
        """Flask-Login needs a method that returns a unique identifier for the user"""
        return self.id  

    @property
    def is_active(self):
        """Return whether the user is active or not"""
        return self.active

    @staticmethod
    def get(id:str):
        return User.find_by_id(id)