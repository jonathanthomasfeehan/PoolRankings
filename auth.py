from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import pymongo.mongo_client
from User import User
import os
import database



auth = Blueprint('auth', __name__)

# client = pymongo.MongoClient('mongodb://%s:%s@database:27017/PoolRankings' % (os.getenv('MONGO_USER'), os.getenv('MONGO_PASSWORD')))
# db = client[os.getenv('MONGO_DB')]

# RECORDS = db.RECORDS
# MATCHES = db.MATCHES
RECORDS = database.RECORDS
MATCHES = database.MATCHES
PENDING_MATCHES =  database.PENDING_MATCHES

@auth.route('/login', methods=['POST', 'GET'])
def login():
    print(f'User is active: {current_user.is_active}')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next = request.form.get('next')
        user = User.find_by_username(username)
        if user and check_password_hash(user.password, password):
            print(f'User is active: {current_user.is_active}')
            login_user(user)
            print(f'User is active: {current_user.is_active}')
            print(f'user name is {current_user.name}')
            # next = 'profile'
            # return("logged in" , 201)
            # return redirect('/profile')
            # return render_template('profile.html')
            next_page = request.args.get('next')
            print(f'Next page is: {next_page}')  # Debug the next parameter

            # Redirect to 'next' or default to the profile page
            print(url_for('profile'))
            print(jsonify({'redirect_url': next_page or url_for('profile')}))
            return jsonify({'redirect_url': next_page or url_for('profile')}), 200

        else:
            print("Failed password")
            return ('Incorrect Password', 470)
    print("NOT POST")
    return render_template('login_page.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


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
    # FIXME:
    try:
        database.db.validate_collection('Users')
        if RECORDS.count_documents({'Username':playerUsername}, limit=1):
                return 'false', 470  
    except pymongo.errors.OperationFailure:
        #creates new record if one does not alreadt exist, stores only the password hash
        result = RECORDS.insert_one({"FirstName": playerFirstName, "LastName": playerLastName, "Username":playerUsername, "Password": generate_password_hash(password),  "Rating": database.STARTING_RATING, "Matches": 0 })    
        if result:
            return 'done', 201
    return 'false', 500

@auth.route('/login_page')
def login_page():
    return render_template('login_page.html')

@auth.route('/changePassword', methods = ["POST"])
@login_required
def changePassword():
    data=request.values
    if not (check_password_hash(current_user.password, data['OldPassword'])):
        return 'Passwords do not match' , 470
    RECORDS.update_one({'Username':data['Username']}, {'$set' : {'Password':generate_password_hash(data['NewPassword'])}})
    return 'Password Updated' , 204


@auth.route('/passwordReset')
def passwordReset():
    return render_template('passwordReset.html')
