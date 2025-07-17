
from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import login_required, current_user, LoginManager, logout_user
import os
import datetime
from app.models.User import User
from app.auth import auth as auth_blueprint
import app.database as database
from flask_cors import CORS
from typing import Callable


def calculate_expected(player1: str, player2: str)->float:
    """
    Calculates likelyhood of player1 winning

    Args: 
        player1 (str): The username of player1 as a string
        player2 (str): The username of player2 as a string
    
    Returns:
        float: Likelyhood that player1 wins match

    Raises:
        google.api_core.GoogleAPICallError
    """
    #calculate expected win rate using elo formula
    # TODO: Ensure that username is unique record in database
    # TODO: Change to database.database_query_one
    try:
        player1_rating = database.database_query(database.USERS, [('Username','==', player1)])
        player2_rating = database.database_query(database.USERS, [('Username','==', player2)])
        player1_rating = player1_rating[0]['Rating']


        player2_rating = player2_rating[0]['Rating']
        player1_expected = (1/(1+(10**( (player2_rating - player1_rating)/database.D))))
        return player1_expected
    except Exception as e:
        print(f'Unable to calculate expected for {player1}')
        raise e

# start of function to add player matches
def report_match(player1: str, player2: str, winner:str) -> bool:
    """
    Calculates and Updates both players new ratings. Inserts new match into matches table

    Args:
        player1: String username for player1
        player2: String username for player2
        winner: String username for winner

    Returns: 
        True on success, False on failure

    Raises: 
        google.api_core.GoogleAPICallError

    """

    # TODO: Update this to hold onto records returned from databaes call. Remove later DB requests
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


    # TODO: database_query_one will either raise an error on exception or return none if no elements are found. Need to adjust this to handle those cases
    player1_old_score = database.database_query_one(database.USERS, [('Username','==', player1)])
    player1_old_score = player1_old_score['Rating']
    player2_old_score = database.database_query_one(database.USERS, [('Username','==', player2)])
    player2_old_score = player2_old_score['Rating']


    # TODO: Pull out into new function for testing, clarity, and future proofing
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
        print(f'Database exception on create/update: {e}')
        raise e

def checkValidOpponent(player1: str, player2: str, db_accessor: Callable[["Firestore_v1.CollectionReference" , list[tuple]] , dict] = database.database_query_one) -> dict:
    """
    # TODO:Implement program docs
    """
    if player2 == player1:
        return {'message': 'Invalid User. Opponent is current user', 'code': 422}
    
    if bool(db_accessor(database.USERS, [('Username', '==', player2)])) == False:
        return {'message': 'Invalid User. User not found', 'code': 403}
    existing_match = (
        db_accessor(database.PENDING_MATCHES, [('Player1', '==', player1), ('Player2', '==', player2), ('Status', '!=', 2)]) or
        db_accessor(database.PENDING_MATCHES, [('Player1', '==', player2), ('Player2', '==', player1), ('Status', '!=', 2)])
    )
    
    if existing_match:
        return {'message': 'Match Already Proposed', 'code': 423}
    
    return {'message': 'Valid User', 'code': 200}



def decreaseTrust(username : str):
    print(f'Decreasing trust in {username}')
    user_id = database.get_user_by_username(username)['id']
    database.database_increment(database.USERS, user_id, 'DisputedMatches', 1)
    database.database_increment(database.USERS, user_id, 'Matches', 1)


