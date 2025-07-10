
from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import login_required, current_user, LoginManager, logout_user
import os
import datetime
from app.models.User import User
from app.auth import auth as auth_blueprint
import app.database as database
from flask_cors import CORS

# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', default=True).lower() == 'true'
# app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', default=True).lower() == 'true'
# app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', default='Lax')
# app.config['PREFERRED_URL_SCHEME']='https'

# csrf = CSRFProtect(app)
# CORS(app)
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# login_manager.init_app(app)
# app.register_blueprint(auth_blueprint)
# app.register_blueprint(main_blueprint)

# @login_manager.user_loader
# def load_user(user_id):
#         return User.get(user_id)




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
    player1_old_score = player1_old_score['Rating']
    player2_old_score = database.database_query_one(database.USERS, [('Username','==', player2)])
    player2_old_score = player2_old_score['Rating']
    if player1_old_score == None or player2_old_score == None:
        return False

    player1_new_score = player1_old_score + database.K*(result[0]-player1_expected)
    player2_new_score = player2_old_score + database.K*(result[1]-player2_expected)

    # TODO: Check if logic should be moved to database module
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


def checkValidOpponent(data):
    if data['PlayerUsername2'] == current_user.username:
        return 'Invalid User. Opponent is current user' , 422
    if database.database_query_one(database.USERS, [('Username','==', data['PlayerUsername2'])]) == None:
        return 'Invalid User. User not found' , 403
    if database.database_query_one(database.PENDING_MATCHES, [('Player1','==',current_user.username),('Player2','==',data['PlayerUsername2']),('Status' , '!=' , 2)]) != None or database.database_query_one(database.PENDING_MATCHES, [('Player1','==',data['PlayerUsername2']),('Player2','==',current_user.username),('Status' , '!=' , 2)]) != None:
        # Check if match already proposed by either player
        return 'Match Already Proposed' , 423
    return 'Valid User' , 200


def decreaseTrust(username : str):
    print(f'Decreasing trust in {username}')
    user_id = database.get_user_by_username(username)['id']
    database.database_increment(database.USERS, user_id, 'DisputedMatches', 1)
    database.database_increment(database.USERS, user_id, 'Matches', 1)


