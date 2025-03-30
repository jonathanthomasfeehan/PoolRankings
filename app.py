
from pydoc import render_doc
from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import login_required, current_user, LoginManager
import pymongo
import pymongo.mongo_client
from werkzeug.security import generate_password_hash, check_password_hash
# TODO clean up excess imports
import os
import datetime
from flask_wtf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
import json
from modules.User import User
from modules.auth import auth as auth_blueprint
import modules.database as database
from flask_cors import CORS
from bson.objectid import ObjectId


app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

main_blueprint = Blueprint('main', __name__)
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
PENDING_MATCHES =  database.PENDING_MATCHES
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

@app.route('/ProposeMatch')
def proposeMatch_page():
    #render match reporting page
    return render_template('ProposeMatch.html')


def calculate_expected(player1, player2):
    #calculate expected win rate using elo formula
    return (1/(1+(10**( (RECORDS.find_one({'Username':player2})['Rating'] - RECORDS.find_one({'Username':player1})['Rating'])/database.D))))


### start of function to add player matches
def report_match(player1: str, player2: str, winner:str) -> bool:

    if RECORDS.find_one({'Username':player1}) == None or RECORDS.find_one({'Username':player2}) == None:
        return False

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
        return False


    player1_old_score = RECORDS.find_one({"Username":player1})['Rating']
    player2_old_score = RECORDS.find_one({"Username":player2})['Rating']

    player1_new_score = player1_old_score + database.K*(result[0]-player1_expected)
    player2_new_score = player2_old_score + database.K*(result[1]-player2_expected)

    try :
        # Update records and catch exceptions
        MATCHES.insert_one({"Player1":player1,"Player2":player2,"Player1_previous_score":player1_old_score,"Player2_previous_score":player2_old_score,"Player1_new_score":player1_new_score,"Player2_new_score":player2_new_score,"Date":datetime.datetime.now()})
        RECORDS.update_one({"Username":player1},{"$set" :{"Rating": (player1_new_score), "Matches": (RECORDS.find_one({'Username':player1})['Matches']+1)}})
        RECORDS.update_one({"Username":player2},{"$set" :{"Rating": (player2_new_score), "Matches": (RECORDS.find_one({'Username':player2})['Matches']+1)}})
        return True
    except Exception as e:
        print(f'Database exception: {e}')
        raise e



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

@app.route('/pendingMatches')
@login_required
def pendingMatches():
    return render_template('pendingMatches.html', name = current_user.name, username = current_user.username)


@app.route('/proposeMatchRequest', methods = ["POST"])
@login_required
def proposeMatchRequest():
    data=request.values
    # TODO: Move database queries to database.py
    if data['PlayerUsername2'] == current_user.username:
        return 'Invalid User. Opponent is current user' , 422
    if RECORDS.find_one({'Username':data['PlayerUsername2']}) == None:
        return 'Invalid User. User not found' , 403
    if PENDING_MATCHES.find_one({"$or" : [{"Player1":current_user.username,"Player2":data['PlayerUsername2']},{"Player1":data['PlayerUsername2'],"Player2":current_user.username}]}):
        return 'Match Already Proposed' , 403
    PENDING_MATCHES.insert_one({"Player1":current_user.username,"Player2":data['PlayerUsername2'],"Status":0, "Date_Proposed":datetime.datetime.now(), "Date_Expired":datetime.datetime.now() + datetime.timedelta(days=3)})
    return 'done' , 200

@app.route('/getProposedMatches', methods = ['POST'])
@login_required
def getProposedMatches():
    # result_data = {'matches' : list(PENDING_MATCHES.find({"Player2":current_user.username}))}
    result_data = list(PENDING_MATCHES.find({'$or' : [{"Player2":current_user.username},{"Player1":current_user.username}]}))

    #  {"Player1":1,"Player2":1,"Date_Proposed":1,"_id": }
    for result in result_data:
        result['_id'] = str(result['_id'])
    print(result_data)
    return {'matches':result_data}, 200

@app.route('/acceptProposedMatch', methods = ["POST"])
@login_required
def acceptProposedMatch():
    data=request.values
    match_id = data['match_id']
    DB_result = PENDING_MATCHES.update_one({'_id' : ObjectId(match_id)},{'$set' : {'Status':1}})
    print(f' Ack\'ed {DB_result.acknowledged}')
    print(f' Matched entries {DB_result.matched_count}')
    return 'done' , 200

@app.route('/rejectProposedMatch', methods = ["POST"])
@login_required
def rejectProposedMatch():
    data=request.values
    match_id = data['match_id']
    DB_result = PENDING_MATCHES.update_one({'_id' : ObjectId(match_id)},{'$set' : {'Status':2}})
    print(f' Ack\'ed {DB_result.acknowledged}')
    print(f' Matched entries {DB_result.matched_count}')
    return 'done' , 200

@app.route('/MarkWinnerPage', methods = ["GET"])
@login_required
def MarkWinnerPage():
    data=request.args
    match_details = (PENDING_MATCHES.find_one({"_id":ObjectId(data['match_id'])}))
    opponent = ''
    if(current_user.username==match_details['Player1']):
        opponent = match_details['Player2']
    else:
        opponent = match_details['Player1']
    return render_template('markWinner.html', username = current_user.username, match_id = data['match_id'], name = current_user.name, opponent=opponent)

@app.route('/sendWinner', methods = ['POST'])
@login_required
def sendWinner():
    data=request.values
    match_id = data['match_id']
    match_details = (PENDING_MATCHES.find_one({"_id":ObjectId(match_id)}))
    if ((current_user.username != match_details['Player1']) and (current_user.username != match_details['Player2'])):
        return 'Incorrect user' , 403

    # Refactor reportMatch function to accept a list and then call it here
    # Need to keep track of marked winner whens status != 3 or 4
    # Need to udpate user field to track disputed matches
    print(match_details)
    print(data)
    if(current_user.username == match_details['Player1']):
        # User is proposer of match
        if(match_details['Status'] == 1):
            # Accepted, no winner yet
            # Set status to 3, Keep track of winner?
            PENDING_MATCHES.update_one({'_id' : ObjectId(match_id)},{'$set' : {'Status':3, 'Winner':data['Winner']}})
            return 'Record Updated' , 200
        elif(match_details['Status']==4):
            # Opponent has already recorded match
            # Calculate match and remove from pending matches
            if(data['Winner'] != match_details['Winner']):
                PENDING_MATCHES.delete_one({'_id':ObjectId(match_id)})
                # Decrease trust in players
                decreaseTrust(match_details['Player1'])
                decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
                PENDING_MATCHES.delete_one({'_id':ObjectId(match_id)})
                return 'Record Updated' , 200

            except:
                return 'Database Failed' , 503
    else:
        # Current user is player2, ie proposed player
        if(match_details['Status'] == 1):
            # No one has recorded match yet. Set status to 4
            PENDING_MATCHES.update_one({'_id' : ObjectId(match_id)},{'$set' : {'Status':4, 'Winner':data['Winner']}})
            return 'Record Updated' , 200
        elif(match_details['Status']==3):
            # Opponent has already recorded, process match and remove from table
            if(data['Winner'] != match_details['Winner']):
                PENDING_MATCHES.delete_one({'_id':ObjectId(match_id)})
                # Decrease trust in players
                decreaseTrust(match_details['Player1'])
                decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
                PENDING_MATCHES.delete_one({'_id':ObjectId(match_id)})
                return 'Record Updated' , 200
            except:
                return 'Database Failed' , 503

def decreaseTrust(username : str):
    print(f'Decreasing trust in {username}')
    RECORDS.update_one({'Username':username}, {'$inc' : {'DisputedMatches':1, 'Matches':1}})


                



app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching of static files




#use for local development
if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)
