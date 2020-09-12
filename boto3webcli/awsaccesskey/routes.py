from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,mail,safe_seralizer,login_manager
from flask_login import login_user, current_user, logout_user, login_required
from boto3webcli.models import User

#Blueprint object
blue = Blueprint('awsaccesskey',__name__,template_folder='templates')

@blue.route('/awsaccesskey')
def awsaccesskey_home():
	return render_template('awsaccesskey/awsaccesskey_home.html',title="Access Key")
