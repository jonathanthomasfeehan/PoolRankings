
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
import datetime

from app import database
from app import logic
import app.logic as logic
import app.auth as auth

main = Blueprint('main', __name__)

@main.route('/')
def index():
    print("Serving index page")
    #render homepage
    return render_template("index.html", isloggedin = current_user.is_active)


@main.route('/ProposeMatch')
def proposeMatch_page():
    #render match reporting page
    return render_template('ProposeMatch.html', name = current_user.name, displayUsername = current_user.displayUsername, username = current_user.username, isloggedin = current_user.is_active)


@main.route('/showRankings')
def displayRankings():
    data = database.database_query(database.USERS, filters=[], fields= ['Rating', 'FirstName', 'LastName','Username','DisplayUsername'])
    # Sort data by rating in descending order
    final = []
    for record in data:
        print(record)
        if record['DisplayUsername'] == 'true':
            final.append({
                'Rating': record['Rating'],
                'FirstName': record['Username'],
            })
        else:
            final.append({
                'Rating': record['Rating'],
                'FirstName': record['FirstName'],
                'LastName': record['LastName'],
            })
    if not current_user.is_anonymous:
        return render_template('showRankings.html', scores=final, name = current_user.name, displayUsername = current_user.displayUsername, username = current_user.username, isloggedin = current_user.is_active)  
    else:
        # If user is not logged in, display rankings without user-specific data
        return render_template('showRankings.html', scores=final, name = '', displayUsername = '', username = '', isloggedin = False)



@main.route('/getRankings' , methods = ['POST'])
def getRankings():
    # TODO: Return ratings in order
    # TODO: Catch errors here
    data = database.database_query(database.USERS, filters=[], fields= ['Rating', 'FirstName', 'LastName'])
    print(data)
    data = jsonify(data)
    return data, 200


@main.route('/register')
def show_registration():
    return render_template('register.html')


@main.route('/getUsernames')
def getUsernames():
    result = database.database_query(database.USERS, filters=[], fields=['Username'])
    data = jsonify(result)
    return data, 200


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name, displayUsername = current_user.displayUsername, username = current_user.username, isloggedin = current_user.is_active)


@main.route('/getUserMatchHistory', methods = ["POST"])
@login_required
def getUserMatchHistory():
    results = database.database_query(database.MATCHES, [('Player1' , '==' , current_user.username)])
    results = results + (database.database_query(database.MATCHES, [('Player2' , '==' , current_user.username)]))
    results = {'matches' : results}
    results['requester'] = current_user.username
    return jsonify(results)


@main.route('/setDisplayUsername', methods = ["POST"])
@login_required
def setDisplayUsername():
    data = request.values
    if data['DisplayUsername'] == None:
        return 'Invalid Display Username', 422
    database.database_update(database.USERS, current_user.id, {'DisplayUsername':data['DisplayUsername']})
    return 'done', 200


@main.route('/pendingMatches')
@login_required
def pendingMatches():
    return render_template('pendingMatches.html',  name = current_user.name, displayUsername = current_user.displayUsername, username = current_user.username, isloggedin = current_user.is_active)


@main.route('/proposeMatchRequest', methods = ["POST"])
@login_required
def proposeMatchRequest():
    data=request.values
    player1 = data['PlayerUsername1']
    player2 = data['PlayerUsername2']
    opponentCheck = logic.checkValidOpponent(player1, player2)
    if opponentCheck["code"] != 200:
        return opponentCheck["message"], opponentCheck["code"]
    database.database_create(database.PENDING_MATCHES, {
        "Player1": current_user.username,
        "Player2": player2,
        "Status": 0,
        "Date_Proposed": datetime.datetime.now(),
        "Date_Expired": datetime.datetime.now() + datetime.timedelta(days=3)
    })
    return 'done' , 200


@main.route('/getProposedMatches', methods = ['POST'])
@login_required
def getProposedMatches():
    # result_data = {'matches' : list(PENDING_MATCHES.find({"Player2":current_user.username}))}

    result_data = database.database_query(database.PENDING_MATCHES, [('Player1','==',current_user.username)])
    result_data += database.database_query(database.PENDING_MATCHES, [('Player2','==',current_user.username)])
    return {'matches':result_data}, 200


@main.route('/acceptProposedMatch', methods = ["POST"])
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


@main.route('/rejectProposedMatch', methods = ["POST"])
@login_required
def rejectProposedMatch():
    data=request.values
    match_id = data['match_id']
    database.database_update(database.PENDING_MATCHES, match_id, {'Status':2})
    # Check if update is successful
    return 'done' , 200


@main.route('/MarkWinnerPage', methods = ["GET"])
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


@main.route('/sendWinner', methods = ['POST'])
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
                logic.decreaseTrust(match_details['Player1'])
                logic.decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                main.report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
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
                logic.decreaseTrust(match_details['Player1'])
                logic.decreaseTrust(match_details['Player2'])
                return 'Winner Mismatch' , 450
            try:
                logic.report_match(player1=match_details['Player1'], player2=match_details['Player2'], winner=match_details['Winner'])
                database.database_delete(database.PENDING_MATCHES, match_id)
                return 'Record Updated' , 200
            except:
                return 'Database Failed' , 503
            

@main.route('/deleteAccount')
@login_required
def deleteAccountPage():
    return render_template('deleteAccount.html' )





@main.route('/healthz' , methods = ["GET"]) 
def healthz():
    if database.database_query(database.USERS, filters=[], fields= ['Username']) == None:
        return 'Database not connected', 500
    return 'OK', 200

