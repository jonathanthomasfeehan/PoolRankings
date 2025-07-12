from unittest.mock import patch, MagicMock

def test_login_logic(client):
    """Test the login logic by mocking the user loader."""
    # TODO: Patch the user loader to return a mock user
    # response = client.get('/login')
    # assert response.status_code == 200
    # assert b'Login' in response.data

def test_login_logic_invalid_user(client):
    """Test the login logic with an invalid user."""
    # TODO: Change to post
    # with patch('app.logic.User.find_by_id', return_value=None):
    #     response = client.get('/login')
    #     assert response.status_code == 404
    #     assert b'User not found' in response.data


def test_login_logic_loggedin(client, logged_in_user):
    """Test the login logic when user is already logged in."""
    # with patch('app.logic.User.find_by_id', return_value=logged_in_user):
    #     response = client.get('/login')
    #     assert response.status_code == 200
    #     assert b'Already logged in' in response.data

def test_logout_logic(client, logged_in_user):
    """Test the logout logic."""
    # with patch('app.logic.User.find_by_id', return_value=logged_in_user):
    #     response = client.get('/logout')
    #     assert response.status_code == 302  # Redirect after logout
    #     assert b'Logged out successfully' in response.data

def test_addNewPlayer_logic(client):
    """Test the addNewPlayer logic."""
    # Mock the database call to check if user exists
    # with patch('app.database.get_user_by_username', return_value=None):
    #     response = client.post('/addNewPlayer', data={
    #         'PlayerFirstName': 'John',
    #         'PlayerLastName': 'Doe',
    #         'PlayerUsername': 'johndoe',
    #         'Password': 'password123',
    #         'Password_confirmation': 'password123'
    #     })
    #     assert response.status_code == 200
    #     assert b'User created successfully' in response.data

def test_loginPage_rendered(captured_templates, client):
    """Test that the login page is rendered correctly."""
    # response = client.get('/login')
    # assert response.status_code == 200
    # assert len(captured_templates) == 1
    # template, context = captured_templates[0]
    # assert template.name == 'login_page.html'
    # assert context['title'] == 'Login Page'
    # assert context['form'] is not None  # Assuming a form is passed to the template

def test_changePassword_logic(client, logged_in_user):
    """Test the change password logic."""
    # with patch('app.logic.User.find_by_id', return_value=logged_in_user):
    #     response = client.post('/changePassword', data={
    #         'current_password': 'oldpassword',
    #         'new_password': 'newpassword123',
    #         'confirm_new_password': 'newpassword123'
    #     })
    #     assert response.status_code == 200
    #     assert b'Password changed successfully' in response.data

def test_resetPasswordPage_rendered(captured_templates, client):
    """Test that the reset password page is rendered correctly."""
    # response = client.get('/resetPassword')
    # assert response.status_code == 200
    # assert len(captured_templates) == 1
    # template, context = captured_templates[0]
    # assert template.name == 'reset_password.html'
    # assert context['title'] == 'Reset Password'
    # assert context['form'] is not None  # Assuming a form is passed to the template