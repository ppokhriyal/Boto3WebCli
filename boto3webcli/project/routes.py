from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.models import User,Project,AccessKey

#Blueprint object
blue = Blueprint('project',__name__,template_folder='templates')


#Project Home
@blue.route('/project')
def project_home():
	return render_template('project/project_home.html',title='Project')