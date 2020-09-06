from flask import Flask

#App Config
app = Flask(__name__)
app.config['SECRET_KEY'] = '878436c0a462c4145fa59eec2c43a66a'


#Import Blueprint routes objects
from boto3webcli.user_management.routes import blue

#Register Blueprint
app.register_blueprint(user_management.routes.blue,url_prefix='/')