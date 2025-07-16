from unittest.mock import patch, MagicMock

def test_index_page(client):
    """Test the index page of the application."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Rack It Up' in response.data


def test_propose_match_page(client, logged_in_user):
    """Test the propose match page of the application."""

    response = client.get('/ProposeMatch')
    assert response.status_code == 200
    assert b'Propose Match' in response.data
    pass

@patch("app.database.database_query", return_value = [{'Rating': 500, 'FirstName': "Test User", 'LastName': "User",'Username': "testuser",'DisplayUsername': True}])
def test_show_rankings_loggedin(database_mock_query, client, captured_templates, logged_in_user):
    """Test the show rankings page of the application."""
    # Look into mocking the database if needed
    response = client.get('/showRankings')
    assert len(captured_templates) == 1
    for template in captured_templates:
        template, context = template
        if template == 'showRankings.html':
            assert context['FirstName'] == logged_in_user.name
            assert context['DisplayUsername'] == logged_in_user.displayUsername
            assert context['Username'] == logged_in_user.username
            assert context['isloggedin'] == logged_in_user.is_active
    assert response.status_code == 200
    assert b'Rankings' in response.data

def test_show_rankings_notloggedin(client, captured_templates):
    """Test the show rankings page of the application when not logged in."""
    response = client.get('/showRankings')
    assert len(captured_templates) == 1
    assert response.status_code == 200
    assert b'Rankings' in response.data



def test_get_rankings(client):
    """Test the get rankings endpoint of the application."""
    # Mocking the database query to return a sample response
    # TODO: test that it works with emulated database
    # with patch('app.database.database_query') as mock_query:
    #     mock_query.return_value = [
    #         {'Rating': 1500, 'FirstName': 'John', 'LastName': 'Doe'},
    #         {'Rating': 1400, 'FirstName': 'Jane', 'LastName': 'Smith'}
    #     ]
    #     response = client.post('/getRankings')
    #     assert response.status_code == 200
    #     data = response.get_json()
    #     assert len(data) == 2
    #     assert data[0]['Rating'] == 1500
    #     assert data[1]['FirstName'] == 'Jane'

def test_register_page(client):
    """Test the registration page of the application."""
    # response = client.get('/register')
    # assert response.status_code == 200
    # assert b'Register' in response.data
# def get_rankings(client):
#     """Test the show rankings page of the application."""
#     # Look into mocking the database if needed
#     response = client
#     assert response.status_code == 200
#     assert b'Propose Match' in response.data

def test_get_usernames(client):
    """Test the get usernames endpoint of the application."""
    # Mocking the database query to return a sample response
    # with patch('app.database.database_query') as mock_query:
    #     mock_query.return_value = [{'Username': 'user1'}, {'Username': 'user2'}]
    #     response = client.get('/getUsernames')
    #     assert response.status_code == 200
    #     data = response.get_json()
    #     assert len(data) == 2
    #     assert data[0]['Username'] == 'user1'
    #     assert data[1]['Username'] == 'user2'

def test_profile_logged_in(client, logged_in_user):
    """Test the profile page of the application when logged in."""
    # response = client.get('/profile')
    # assert response.status_code == 200
    # assert b'Profile' in response.data
    # assert b'Welcome, Test User' in response.data

def test_profile_not_logged_in(client):
    """Test the profile page of the application when not logged in."""
    # response = client.get('/profile')
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Redirecting...' in response.data
    # assert b'Login' in response.data  # Check if login link is present


def test_getUserMatchHistory_logged_in(client, logged_in_user):
    """Test the get user match history endpoint of the application."""
    # Mocking the database query to return a sample response
    # with patch('app.database.database_query') as mock_query:
    #     # TODO: check these values
    #     mock_query.return_value = [
    #         {'Player1': 'user1', 'Player2': 'user2', 'Winner': 'user1'},
    #         {'Player1': 'user3', 'Player2': 'user4', 'Winner': 'user4'}
    #     ]
    #     response = client.post('/getUserMatchHistory')
    #     assert response.status_code == 200
    #     data = response.get_json()
    #     assert len(data) == 2
    #     assert data[0]['Winner'] == 'user1'
    #     assert data[1]['Player2'] == 'user4'

def test_getUserMatchHistory_not_logged_in(client):
    """Test the get user match history endpoint of the application when not logged in."""
    # response = client.post('/getUserMatchHistory')
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_setDisplayUsername(client, logged_in_user):
    """Test the set display username endpoint of the application."""
    # with patch('app.database.database_update') as mock_update:
    #     response = client.post('/setDisplayUsername', data={'DisplayUsername': 'new_display'})
    #     assert response.status_code == 200
    #     mock_update.assert_called_once_with('USERS', logged_in_user.id, {'DisplayUsername': 'new_display'})

def test_setDisplayUsername_not_logged_in(client):
    """Test the set display username endpoint of the application when not logged in."""
    # response = client.post('/setDisplayUsername', data={'DisplayUsername': 'new_display'})
    # assert response.status_code == 302  # Redirect to login page

def test_pendingMatches_logged_in(client, logged_in_user):
    """Test the pending matches page of the application when logged in."""
    # response = client.get('/pendingMatches')
    # assert response.status_code == 200
    # assert b'Pending Matches' in response.data
    # assert b'Welcome, Test User' in response.data

def test_pendingMatches_not_logged_in(client):
    """Test the pending matches page of the application when not logged in."""
    # response = client.get('/pendingMatches')
    # assert response.status_code == 302  # Redirect to login page

def test_proposeMatchRequest_logged_in(client, logged_in_user):
    """Test the propose match request endpoint of the application when logged in."""
    # TODO: Update this test to mock the database and check the response
    # with patch('app.logic.checkValidOpponent') as mock_check:
    #     mock_check.return_value = ('Valid User', 200)
    #     response = client.post('/proposeMatchRequest', data={'PlayerUsername2': 'opponent'})
    #     assert response.status_code == 200
    #     mock_check.assert_called_once_with({'PlayerUsername2': 'opponent'})

def test_proposeMatchRequest_not_logged_in(client):
    """Test the propose match request endpoint of the application when not logged in."""
    # response = client.post('/proposeMatchRequest', data={'PlayerUsername2': 'opponent'})
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_getProposedMatches_logged_in(client, logged_in_user):
    """Test the get proposed matches endpoint of the application when logged in."""
    # Mocking the database query to return a sample response
    # with patch('app.database.database_query') as mock_query:
    #     mock_query.return_value = [
    #         {'Player1': 'user1', 'Player2': 'user2', 'Status': 0},
    #         {'Player1': 'user3', 'Player2': 'user4', 'Status': 1}
    #     ]
    #     response = client.post('/getProposedMatches')
    #     assert response.status_code == 200
    #     data = response.get_json()
    #     assert len(data) == 2
    #     assert data[0]['Status'] == 0
    #     assert data[1]['Player2'] == 'user4'

def test_getProposedMatches_not_logged_in(client):
    """Test the get proposed matches endpoint of the application when not logged in."""
    # response = client.post('/getProposedMatches')
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_acceptProposedMatch_logged_in(client, logged_in_user):
    """Test the accept proposed match endpoint of the application when logged in."""
    # with patch('app.database.database_update') as mock_update:
    #     response = client.post('/acceptProposedMatch', data={'match_id': '123'})
    #     assert response.status_code == 200
    #     mock_update.assert_called_once_with('PENDING_MATCHES', '123', {'Status': 1})

def test_acceptProposedMatch_not_logged_in(client):
    """Test the accept proposed match endpoint of the application when not logged in."""
    # response = client.post('/acceptProposedMatch', data={'match_id': '123'})
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_rejectProposedMatch_logged_in(client, logged_in_user):
    """Test the reject proposed match endpoint of the application when logged in."""
    # with patch('app.database.database_update') as mock_update:
    #     response = client.post('/rejectProposedMatch', data={'match_id': '123'})
    #     assert response.status_code == 200
    #     mock_update.assert_called_once_with('PENDING_MATCHES', '123', {'Status': 2})

def test_rejectProposedMatch_not_logged_in(client): 
    """Test the reject proposed match endpoint of the application when not logged in."""
    # response = client.post('/rejectProposedMatch', data={'match_id': '123'})
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_markWinnerPage_logged_in(client, logged_in_user):
    """Test the mark winner page of the application when logged in."""
    # response = client.get('/MarkWinnerPage?match_id=123')
    # assert response.status_code == 200
    # assert b'Mark Winner' in response.data
    # assert b'Welcome, Test User' in response.data

def test_markWinnerPage_not_logged_in(client):
    """Test the mark winner page of the application when not logged in."""
    # response = client.get('/MarkWinnerPage?match_id=123')
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_sendWinner_logged_in(client, logged_in_user):
    """Test the send winner endpoint of the application when logged in."""
    # with patch('app.database.database_update') as mock_update:
    #     response = client.post('/sendWinner', data={'match_id': '123', 'Winner': 'user1'})
    #     assert response.status_code == 200
    #     mock_update.assert_called_once_with('PENDING_MATCHES', '123', {'Status': 3, 'Winner': 'user1'})

def test_sendWinner_not_logged_in(client):
    """Test the send winner endpoint of the application when not logged in."""
    # response = client.post('/sendWinner', data={'match_id': '123', 'Winner': 'user1'})
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_deleteAccount_logged_in(client, logged_in_user):
    """Test the delete account endpoint of the application when logged in."""
    # with patch('app.database.database_delete') as mock_delete:
    #     response = client.post('/deleteAccount')
    #     assert response.status_code == 200
    #     mock_delete.assert_called_once_with('USERS', logged_in_user.id)

def test_deleteAccount_not_logged_in(client):
    """Test the delete account endpoint of the application when not logged in."""
    # response = client.post('/deleteAccount')
    # assert response.status_code == 302  # Redirect to login page
    # assert b'Login' in response.data  # Check if login link is present

def test_health_check(client):
    """Test the health check endpoint of the application."""
    # response = client.get('/healthz')
    # assert response.status_code == 200
    # assert b'OK' in response.data

