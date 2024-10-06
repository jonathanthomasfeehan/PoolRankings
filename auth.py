from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import pymongo.mongo_client
from User import User
import os



auth = Blueprint('auth', __name__)

client = pymongo.MongoClient('mongodb://%s:%s@database:27017/PoolRankings' % (os.getenv('MONGO_USER'), os.getenv('MONGO_PASSWORD')))
db = client[os.getenv('MONGO_DB')]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.find_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            next = 'profile'
            return redirect('/profile')
            #return redirect('/profile')
        else:
            return (470)
    return render_template('login_page.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/addNewPlayer', methods = ["POST"])
def addNewPlayer():
    #processes request to get data
    data = request.form

    #saves name that needs to be added
    playerFirstName = data['PlayerFirstName']
    playerLastName = data['PlayerLastName']
    playerUsername = data['PlayerUsername']
    password = data['Password']
    password_confirmation = data['Password_confirmation']

    if(password != password_confirmation):
        return 'false', 406
    
    # checks to see if name exists in database already
    try:
        db.validate_collection('Users')
        if RECORDS.count_documents({'Username':playerUsername}, limit=1):
                return 'false', 470  
    except pymongo.errors.OperationFailure:
        #creates new record if one does not alreadt exist, stores only the password hash
        result = RECORDS.insert_one({"FirstName": playerFirstName, "LastName": playerLastName, "Username":playerUsername, "Password": generate_password_hash(password),  "Rating": STARTING_RATING, "Matches": 0 })    
        if result:
            return 'done', 201
    return 'false', 500

@auth.route('/login_page')
def login_page():
    return render_template('login_page.html')