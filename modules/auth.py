from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from modules.User import User
import modules.database as database



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    print(f"Session: {User.is_authenticated}")  # should trigger cookie creation

    if request.method == 'POST':
        print("In login POST")
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.find_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            print(f'User is active: {current_user.is_active}')
            print(f'user name is {current_user.name}')
            next_page = request.args.get('next')
            # Not really used as nav buttons leading to locked pages arent present if not logged in
            return jsonify({'redirect_url': next_page or url_for('profile')}), 200

        else:
            print("Failed password")
            return ('Incorrect Password', 470)
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
    # Need to get USER document ids to check if they exist
    if database.get_user_by_username(playerUsername):
        return 'false', 470
        #creates new record if one does not alreadt exist, stores only the password hash
    result = database.database_create(database.USERS,  
        {"FirstName": playerFirstName, 
        "LastName": playerLastName, 
        "Username":playerUsername, 
        "Password": generate_password_hash(password),  
        "Rating": database.STARTING_RATING, 
        "Matches": 0, 
        "DisputedMatches": 0,
        "DisplayUsername":"true" })
    if result == None:
        return 'false', 470
    
    login_data = {'username': playerUsername, 'password': password}
    return login_data, 201

@auth.route('/login_page')
def login_page():
    return render_template('login_page.html')

@auth.route('/changePassword', methods = ["POST"])
@login_required
def changePassword():
    data=request.values
    if not (check_password_hash(current_user.password, data['OldPassword'])):
        return 'Passwords do not match' , 470
    database.database_update(database.USERS, current_user.id, {'Password':generate_password_hash(data['NewPassword'])})
    return 'Password Updated' , 204


@auth.route('/passwordReset')
def passwordReset():
    return render_template('passwordReset.html')
