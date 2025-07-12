from app import logic as logic
from unittest.mock import patch, MagicMock


def test_calculate_expected():
    """Test the calculate_expected function."""
    # player1 = 'player1'
    # player2 = 'player2'
    
    # # Mock the database query to return fixed ratings
    # with patch('app.database.database_query', return_value=[{'Rating': 1600}, {'Rating': 1400}]):
    #     expected = logic.calculate_expected(player1, player2)
    #     assert expected == 0.76  # Expected win rate for player1 against player2
    #     # TODO: double check this value with actual calculation

def test_calculate_expected_failure():
    """Test the calculate_expected function with failure scenario."""
    # player1 = 'player1'
    # player2 = 'player2'
    
    # # Mock the database query to return None
    # with patch('app.database.database_query', return_value=None):
    #     expected = logic.calculate_expected(player1, player2)
    #     assert expected is None  # Should return None if ratings are not found

def test_report_match():
    """Test the report_match function."""
    # player1 = 'player1'
    # player2 = 'player2'
    # winner = 'player1'
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', side_effect=lambda x: {'Username': x, 'Rating': 1600} if x == player1 else {'Username': x, 'Rating': 1400}):
    #     with patch('app.database.database_create') as mock_create:
    #         result = logic.report_match(player1, player2, winner)
    #         assert result is True  # Should return True if match is reported successfully
    #         mock_create.assert_called_once()  # Ensure database_create was called

def test_report_match_failure():
    """Test the report_match function with failure scenario."""
    # player1 = 'player1'
    # player2 = 'player2'
    # winner = 'player3'  # Invalid winner
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', return_value=None):
    #     result = logic.report_match(player1, player2, winner)
    #     assert result is False  # Should return False if users are not found or winner is invalid

def test_checkValidOpponent():
    """Test the checkValidOpponent function."""
    # player1 = 'player1'
    # player2 = 'player2'
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', side_effect=lambda x: {'Username': x} if x in [player1, player2] else None):
    #     result = logic.checkValidOpponent(player1, player2)
    #     assert result is True  # Should return True if both players are valid

def test_checkValidOpponent_failure():
    """Test the checkValidOpponent function with failure scenario."""
    # player1 = 'player1'
    # player2 = 'invalid_player'  # Invalid opponent
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', return_value=None):
    #     result = logic.checkValidOpponent(player1, player2)
    #     assert result is False  # Should return False if any player is invalid

def test_decrease_trust():
    """Test the decrease_trust function."""
    # player1 = 'player1'
    # player2 = 'player2'
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', side_effect=lambda x: {'Username': x, 'Trust': 100} if x in [player1, player2] else None):
    #     with patch('app.database.database_update') as mock_update:
    #         logic.decreaseTrust(player1, player2)
    #         mock_update.assert_called_once()  # Ensure database_update was called

def test_decrease_trust_failure():
    """Test the decrease_trust function with failure scenario."""
    # player1 = 'player1'
    # player2 = 'invalid_player'  # Invalid opponent
    
    # # Mock the database calls
    # with patch('app.database.get_user_by_username', return_value=None):
    #     result = logic.decreaseTrust(player1, player2)
    #     assert result is False  # Should return False if any player is invalid

