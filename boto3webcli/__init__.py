from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager

#App Config
app = Flask(__name__)
app.config['SECRET_KEY'] = '878436c0a462c4145fa59eec2c43a66a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config ['SQLALCHEMY_BINDS'] = {'users':'sqlite:///users.db'}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#Login Manager
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'user_management.login'
login_manager.login_message_category = 'info'

#Import Blueprint routes objects
from boto3webcli.user_management.routes import blue

#Register Blueprint
app.register_blueprint(user_management.routes.blue,url_prefix='/')