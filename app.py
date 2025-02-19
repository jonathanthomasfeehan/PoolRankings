
from pydoc import render_doc
from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import login_required, current_user, LoginManager
import pymongo
import pymongo.mongo_client
from werkzeug.security import generate_password_hash, check_password_hash
# TODO clean up excess imports
import auth
import os
import datetime
from flask_wtf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import urllib
from User import User
from auth import auth as auth_blueprint
import database
from flask_cors import CORS




# def get_app_secret():

#constants
#Moved to database


app = Flask(__name__)

main_blueprint = Blueprint('main', __name__)

# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
# app.config['SERVER_NAME']='localhost'
# app.config['SECRET_KEY'] = os.urandom(32)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# TODO: Fix for prod
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False 

csrf = CSRFProtect(app)
CORS(app)
# app.register_blueprint(auth.bp)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


RECORDS = database.RECORDS
MATCHES = database.MATCHES
app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)

@login_manager.user_loader
def load_user(user_id):
        return User.get(user_id)

@app.route('/')
def index():
    #TODO: fix function name
    #render homepage
    return render_template("index.html", isloggedin = current_user.is_active)

@app.route('/ReportMatch')
def reportMatch_page():
    #render match reporting page
    return render_template('reportMatch.html')


def calculate_expected(player1, player2):
    #calculate expected win rate using elo formula
    return (1/(1+(10**( (RECORDS.find_one({'Username':player2})['Rating'] - RECORDS.find_one({'Username':player1})['Rating'])/database.D))))


### start of function to add player matches
@app.route('/addMatchToDatabase', methods = ["POST"])
def report_match():
    #Get data from post request


    data=request.values
    # 
    #   
    # Get input
    player1 = data['PlayerUsername1']
    player2 = data["PlayerUsername2"]


    if RECORDS.find_one({'Username':player1}) == None or RECORDS.find_one({'Username':player2}) == None:
        return "Names not found", 400

    winner = data.get("Winner")

    #Calculate expected win rates for both players
    player1_expected = calculate_expected(player1, player2)
    player2_expected = calculate_expected(player2, player1)

    #create tuple based on winner
    if(winner==player1):
        result = (1,0)
    elif(winner==player2):
        result = (0,1)
    #if winner is neither player or null return error code
    else:
        return "No winner selected" , 400


    player1_old_score = RECORDS.find_one({"Username":player1})['Rating']
    player2_old_score = RECORDS.find_one({"Username":player2})['Rating']

    player1_new_score = player1_old_score + database.K*(result[0]-player1_expected)
    player2_new_score = player2_old_score + database.K*(result[1]-player2_expected)

    MATCHES.insert_one({"Player1":player1,"Player2":player2,"Player1_previous_score":player1_old_score,"Player2_previous_score":player2_old_score,"Player1_new_score":player1_new_score,"Player2_new_score":player2_new_score,"Date":datetime.datetime.now()})
    #update database with new ratings
    RECORDS.update_one({"Username":player1},{"$set" :{"Rating": (player1_new_score), "Matches": (RECORDS.find_one({'Username':player1})['Matches']+1)}})
    RECORDS.update_one({"Username":player2},{"$set" :{"Rating": (player2_new_score), "Matches": (RECORDS.find_one({'Username':player2})['Matches']+1)}})

    #return successful code
    return 'done' , 200



@app.route('/showRankings')
def displayRankings():
    data = list(RECORDS.find({},{'Rating':1,'FirstName':1, "LastName":1, '_id':0}))
    print(data)
    return render_template('showRankings.html', scores=data)



@app.route('/getRankings' , methods = ['POST'])
def getRankings():
    data = list(RECORDS.find({},{'Rating':1,'FirstName':1, "LastName":1, '_id':0}))
    data = jsonify(data)
    return data, 200


@app.route('/register')
def show_registration():
    return render_template('register.html')

@app.route('/getUsernames')
def getUsernames():
    result = list(RECORDS.find({},{'Username':1, '_id':0}))
    print(result)
    data = jsonify(result)
    return data, 200


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

@app.route('/getUserMatchHistory', methods = ["POST"])
@login_required
def getUserMatchHistory():
    print("IN function")
    results = {'matches' : list(MATCHES.find({"$or" : [{"Player1" : current_user.username},{"Player2": current_user.username}]}, {"_id":0  }))}
    # TODO: Add which user made request to JSON, pull Player names of opponents, insert requester username into specific slot in matches list
    results['requester'] = current_user.username
    print(results)
    return jsonify(results)



app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching of static files

#use for local development
if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)
