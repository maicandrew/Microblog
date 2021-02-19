import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #SQLite Database configuration variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-flask-key'
    POSTS_PER_PAGE = 3
    MESSAGES_PER_PAGE = 5
    #Configuration variables for emailing errors to ADMINS (for production server only)
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT')) or 25
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #Variable for supported languages
    LANGUAGES = ['en', 'es']
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'