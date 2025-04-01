
from pydoc import render_doc
from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import login_required, current_user, LoginManager
# TODO: clean up excess imports
import os
import datetime
from flask_wtf import CSRFProtect
from modules.User import User
from modules.auth import auth as auth_blueprint
import modules.database as database
from flask_cors import CORS


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
    # TODO: Ensure that username is unique record in database
    player1_rating = database.database_query(database.USERS, [('Username','==', player1)])
    player2_rating = database.database_query(database.USERS, [('Username','==', player2)])
    player1_rating = player1_rating[0]['Rating']
    player2_rating = player2_rating[0]['Rating']
    player1_expected = (1/(1+(10**( (player2_rating - player1_rating)/database.D))))
    return player1_expected

# start of function to add player matches
def report_match(player1: str, player2: str, winner:str) -> bool:

    if database.get_user_by_username(player1) == None or database.get_user_by_username(player2) == None:
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


    player1_old_score = database.database_query_one(database.USERS, [('Username','==', player1)])
    print(f'Player 1 old score: {player1_old_score}')
    player1_old_score = player1_old_score['Rating']
    player2_old_score = database.database_query_one(database.USERS, [('Username','==', player2)])
    print(f'Player 1 old score: {player2_old_score}')
    player2_old_score = player2_old_score['Rating']
    if player1_old_score == None or player2_old_score == None:
        return False

    player1_new_score = player1_old_score + database.K*(result[0]-player1_expected)
    player2_new_score = player2_old_score + database.K*(result[1]-player2_expected)

    try :
        database.database_create(database.MATCHES, {
            "Player1": player1,
            "Player2": player2,
            "Player1_previous_score": player1_old_score,
            "Player2_previous_score": player2_old_score,
            "Player1_new_score": player1_new_score,
            "Player2_new_score": player2_new_score,
            "Date": datetime.datetime.now()
        })

        # Update records and catch exceptions
        database.update_player_rankings(player1, player2, player1_new_score, player2_new_score)
        return True
    except Exception as e:
        print(f'Database exception: {e}')
        raise e



@app.route('/showRankings')
def displayRankings():
    data = database.database_query(database.USERS, filters=[], fields= ['Rating', 'FirstName', 'LastName'])
    print(data)
    return render_template('showRankings.html', scores=data)



@app.route('/getRankings' , methods = ['POST'])
def getRankings():
    # TODO: Return ratings in order
    data = database.database_query(database.USERS, filters=[], fields= ['Rating', 'FirstName', 'LastName'])
    data = jsonify(data)
    return data, 200


@app.route('/register')
def show_registration():
    return render_template('register.html')

@app.route('/getUsernames')
def getUsernames():
    result = database.database_query(database.USERS, filters=[], fields=['Username'])
    # result = database.database_query(database.USERS, filters=[])
    # result = database.USERS.select(['Username']).stream()
    # final_result = []
    # for doc in result:
    #     print(f'returned result: {doc} \n {doc.id} \n {doc.to_dict()} \n')
    #     final_result += [doc.to_dict()]

    # print(final_result)
    data = jsonify(result)
    return data, 200


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

@app.route('/getUserMatchHistory', methods = ["POST"])
@login_required
def getUserMatchHistory():
    results = database.database_query(database.MATCHES, [('Player1' , '==' , current_user.username)])
    results = results + (database.database_query(database.MATCHES, [('Player2' , '==' , current_user.username)]))
    results = {'matches' : results}
    results['requester'] = current_user.username
    # for res in results:
    #     # res.pop("id", None)
    #     # Userid not currently included, but may be useful in the future
    #     res['Requester']=current_user.username

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
    if data['PlayerUsername2'] == current_user.username:
        return 'Invalid User. Opponent is current user' , 422
    if database.database_query_one(database.USERS, [('Username','==', data['PlayerUsername2'])]) == None:
        return 'Invalid User. User not found' , 403
    if database.database_query_one(database.PENDING_MATCHES, [('Player1','==',current_user.username),('Player2','==',data['PlayerUsername2'])]) != None or database.database_query_one(database.PENDING_MATCHES, [('Player1','==',data['PlayerUsername2']),('Player2','==',current_user.username)]) != None:
        # Check if match already proposed by either player
        return 'Match Already Proposed' , 403
    database.database_create(database.PENDING_MATCHES, {
        "Player1": current_user.username,
        "Player2": data['PlayerUsername2'],
        "Status": 0,
        "Date_Proposed": datetime.datetime.now(),
        "Date_Expired": datetime.datetime.now() + datetime.timedelta(days=3)
    })
    return 'done' , 200

@app.route('/getProposedMatches', methods = ['POST'])
@login_required
def getProposedMatches():
    # result_data = {'matches' : list(PENDING_MATCHES.find({"Player2":current_user.username}))}

    result_data = database.database_query(database.PENDING_MATCHES, [('Player1','==',current_user.username)])
    result_data += database.database_query(database.PENDING_MATCHES, [('Player2','==',current_user.username)])
    return {'matches':result_data}, 200

@app.route('/acceptProposedMatch', methods = ["POST"])
@login_required
def acceptProposedMatch():

    data=request.values
    match_id = data['match_id']
    DB_result = database.database_update(database.PENDING_MATCHES, match_id, {'Status':1})
    # Check if update is successful
    print(f'Update result: {DB_result}')
    if DB_result == None:
        return 'Error updating match', 500
    return 'done' , 200

@app.route('/rejectProposedMatch', methods = ["POST"])
@login_required
def rejectProposedMatch():
    data=request.values
    match_id = data['match_id']
    database.database_update(database.PENDING_MATCHES, match_id, {'Status':2})
    # Check if update is successful
    return 'done' , 200

@app.route('/MarkWinnerPage', methods = ["GET"])
@login_required
def MarkWinnerPage():
    data=request.args
    match_details = database.database_query_one(database.PENDING_MATCHES, [('id','==',data['match_id'])])
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
    match_details = database.database_query_one(database.PENDING_MATCHES, [('id','==',match_id)])
    if ((current_user.username != match_details['Player1']) and (current_user.username != match_details['Player2'])):
        return 'Incorrect user' , 403

    if(current_user.username == match_details['Player1']):
        # User is proposer of match
        if(match_details['Status'] == 1):
            # Accepted, no winner yet
            # Set status to 3, Keep track of winner?
            database.database_update(database.PENDING_MATCHES, match_id, {'Status':3, 'Winner':data['Winner']})
            return 'Record Updated' , 200
        elif(match_details['Status']==4):
            # Opponent has already recorded match
            # Calculate match and remove from pending matches
            if(data['Winner'] != match_details['Winner']):
                database.database_delete(database.PENDING_MATCHES, match_id)
                # Decrease trust in players
                decreaseTrust(match_details['Player1'])
                decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
                database.database_delete(database.PENDING_MATCHES, match_id)
                return 'Record Updated' , 200

            except:
                return 'Database Failed' , 503
    else:
        # Current user is player2, ie proposed player
        if(match_details['Status'] == 1):
            # No one has recorded match yet. Set status to 4
            database.database_update(database.PENDING_MATCHES, match_id, {'Status':4, 'Winner':data['Winner']})
            return 'Record Updated' , 200
        elif(match_details['Status']==3):
            # Opponent has already recorded, process match and remove from table
            if(data['Winner'] != match_details['Winner']):
                database.database_delete(database.PENDING_MATCHES, match_id)
                # Decrease trust in players
                decreaseTrust(match_details['Player1'])
                decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
                database.database_delete(database.PENDING_MATCHES, match_id)
                return 'Record Updated' , 200
            except:
                return 'Database Failed' , 503

def decreaseTrust(username : str):
    print(f'Decreasing trust in {username}')
    user_id = database.get_user_by_username(username)['id']
    database.database_increment(database.USERS, user_id, 'DisputedMatches', 1)
    database.database_increment(database.USERS, user_id, 'Matches', 1)


#use for local development
if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)
