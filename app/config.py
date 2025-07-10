import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = 'https'

class DevConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    FIREBASE_SECRET_KEY = os.getenv("FIREBASE_SECRET_KEY")

class ProdConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    FIREBASE_SECRET_KEY = os.getenv("FIREBASE_SECRET_KEY")