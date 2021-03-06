import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request #import for instantiating
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch
from redis import Redis
import rq
import os

db = SQLAlchemy() #Instantiates the database and load configration from app
migrate = Migrate() # Used for keeping up-to-date the database
login = LoginManager() #For managing the aussumes the service is running on the same host and in the default port will be used.thenticated
login.login_view = 'auth.login'
login.login_message = _l('You need to be logged in to access this page')
mail = Mail() #For sending emails
bootstrap = Bootstrap() #For using bootstrap and making things look better
moment = Moment() # Format date and time in the user's timezone
babel = Babel() # For translating issues

def create_app(config_class=Config):
    app = Flask(__name__) #Instantiate the app
    app.config.from_object(Config) #Charge configuration from class on the config.py file

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) \
        if app.config['ELASTICSEARCH_URL'] else None
    
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    if not app.debug and not app.testing:
        if app.config.get('MAIL_SERVER',None):
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_SERVER'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='noreply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
        maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

        if not app.config['LOG_TO_STDOUT']:
            streamhandler = logging.StreamHandler()
            streamhandler.setLevel(logging.INFO)
            app.logger.addHandler(streamhandler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                                maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

@babel.localeselector
def get_locale_selector():
    #return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'es'

from app import models #import at the end to avoid circular imports
