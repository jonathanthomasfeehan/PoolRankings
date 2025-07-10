import pytest
import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['LOGIN_DISABLED'] = True  # Disable login during tests
    with flask_app.test_client() as client:
        yield client