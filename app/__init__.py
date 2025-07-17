import os
from flask import Flask

def create_app(config_object=None):
    app= Flask(__name__)

    app.config.from_mapping({
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PREFERED_URL_SCHEME': 'https'
    })
    if config_object:
        app.config.from_object(config_object)

    from flask_login import LoginManager
    from flask_wtf.csrf import CSRFProtect
    from flask_cors import CORS

    CSRFProtect(app)
    CORS(app)

    loginManager = LoginManager()
    loginManager.login_view = 'auth.login'
    loginManager.init_app(app)

    from app.models.User import User
    @loginManager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Register blueprints
    from .routes.auth_routes import auth as auth_blueprint
    from .routes.main_routes import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    app.template_folder='./src/templates'
    app.static_folder='./src/static'

    return app
