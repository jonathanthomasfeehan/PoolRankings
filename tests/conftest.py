import pytest
# from app.routes.main_routes import main as main_blueprint
# from app.routes.auth_routes import auth as auth_blueprint
# from app import create_app
from dotenv import load_dotenv
from app import create_app
from unittest.mock import MagicMock
from flask import template_rendered
# TODO: see if neccesary
load_dotenv('.//.env')


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True  # Disable login during tests
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_user(monkeypatch):
    mock_user= MagicMock()
    mock_user.is_authenticated = True
    mock_user.id = 1
    mock_user.name = 'Test User'
    mock_user.username = 'testuser'
    mock_user.displayUsername = 'Test User'
    mock_user.is_active = True

    monkeypatch.setattr('flask_login.utils._get_user', lambda: mock_user)
    return mock_user

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    yield recorded
    template_rendered.disconnect(record, app)