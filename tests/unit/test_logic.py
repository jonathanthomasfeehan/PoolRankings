from app import logic as logic
import app
from unittest.mock import patch, MagicMock
from google.api_core import exceptions as google_exceptions
import pytest
from flask_login import current_user

import app.database


def test_calculate_expected():
    """Test the calculate_expected function."""
    player1 = MagicMock()
    player2 = MagicMock()
    data_values = [[0.36, 500 ,600],
                   [0.21, 535, 765],
                   [0.89, 468, 100],
                   [0.01, 100, 900]]
    
    for data in data_values:
        player1.__getitem__.side_effect=(lambda x: data[1])
        player2.__getitem__.side_effect=(lambda x: data[2])

        # Mock the database query to return fixed ratings
        with patch('app.database.database_query', side_effect=(lambda x,y: [y[0][2]])):
            expected = logic.calculate_expected(player1, player2)
            print(expected)
            expected = round(expected, 2)
            assert expected == data[0]  # Expected win rate for player1 against player2

@patch("app.database.database_query")
def test_calculate_expected_failure(mock_database_method):
    """Test the calculate_expected function with failure scenario."""
    mock_database_method.side_effect = google_exceptions.GoogleAPICallError("Simulated database failure")
    player1 = "testUser1"
    player2 = "testUser2"
    data_values = [[0.36, 500 ,600],
                   [0.21, 535, 765],
                   [0.89, 468, 100],
                   [0.01, 100, 900]]
    with pytest.raises(google_exceptions.GoogleAPICallError):
        logic.calculate_expected(player1, player2)



@patch('app.database.get_user_by_username')
@patch('app.database.database_create')
@patch('app.database.update_player_rankings')
@patch('app.logic.calculate_expected')
@patch('app.database.database_query_one')
def test_report_match_player1_win(mock_query_one, mock_calculate_expected, mock_update_player_rankings, mock_create, mock_get_user_by_username):
    """Test the report_match function."""
    player1 = 'player1'
    player2 = 'player2'
    winner = 'player1'
    mock_get_user_by_username.side_effect=lambda x: {'Username': x, 'Rating': 1600} if x == player1 else {'Username': x, 'Rating': 1400}
    mock_calculate_expected.return_value = 0.5
    mock_query_one.return_value = {"Rating": 1600}

    # Mock the database calls
    result = logic.report_match(player1, player2, winner)
    assert result is True  # Should return True if match is reported successfully
    mock_create.assert_called_once()  # Ensure database_create was called


@patch('app.database.get_user_by_username')
@patch('app.database.database_create')
@patch('app.database.update_player_rankings')
@patch('app.logic.calculate_expected')
@patch('app.database.database_query_one')
def test_report_match_failure(mock_query_one, mock_calculate_expected, mock_update_player_rankings, mock_create, mock_get_user_by_username):
    """Test the report_match function with failure scenario."""
    player1 = 'player1'
    player2 = 'player2'
    winner = 'player1'
    mock_get_user_by_username.side_effect=lambda x: {'Username': x, 'Rating': 1600} if x == player1 else {'Username': x, 'Rating': 1400}
    mock_calculate_expected.return_value = 0.5
    mock_query_one.return_value = {"Rating": 1600}
    mock_create.side_effect=google_exceptions.GoogleAPICallError("Database Failure")
    # Mock the database calls
    with pytest.raises(Exception):
        logic.report_match(player1, player2, winner)


def test_checkValidOpponent():
    """Test the checkValidOpponent function."""
def test_valid_opponent_passes():
    def access_mocker(table, query):
        if table == app.database.USERS:
            return {"Username": "test_user"}
        elif table == app.database.PENDING_MATCHES:
            return []
    mock_db = MagicMock(side_effect=access_mocker)
    result = logic.checkValidOpponent('alice', 'bob', db_accessor=mock_db)
    assert result == {'message': 'Valid User', 'code': 200}

def test_checkValidOpponent_invalid_input():
    """Test the checkValidOpponent function with failure scenario."""
    def access_mocker(table, query):
        if table == app.database.USERS:
            return {"Username": "test_user"}
        elif table == app.database.PENDING_MATCHES:
            return []
    mock_db = MagicMock(side_effect=access_mocker)
    result = logic.checkValidOpponent('alice', 'alice', db_accessor=mock_db)
    assert result == {'message': 'Invalid User. Opponent is current user', 'code': 422}

def test_checkValidOpponent_pending_match_already():
    """Test the checkValidOpponent function with failure scenario."""
    def access_mocker(table, query):
        if table == app.database.USERS:
            return {"Username": "test_user"}
        elif table == app.database.PENDING_MATCHES:
            # return non-empty list to enter pending matches check
            return [{"PENDINGMATCHES": "EXISTS"}]
    mock_db = MagicMock(side_effect=access_mocker)
    result = logic.checkValidOpponent('alice', 'alice', db_accessor=mock_db)
    assert result == {'message': 'Invalid User. Opponent is current user', 'code': 422}

def test_checkValidOpponent_second_player_doesnt_exist():
    """Test the checkValidOpponent function with failure scenario."""
    def access_mocker(table, query):
        if table == app.database.USERS:
            return {}
        elif table == app.database.PENDING_MATCHES:
            return {}
    mock_db = MagicMock(side_effect=access_mocker)
    result = logic.checkValidOpponent('bob', 'alice', db_accessor=mock_db)
    assert result == {'message': 'Invalid User. User not found', 'code': 403}

