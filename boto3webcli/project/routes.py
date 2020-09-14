from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.project.forms import NewProjectForm
from boto3webcli.models import User,Project,AccessKey

#Blueprint object
blue = Blueprint('project',__name__,template_folder='templates')


#Project Home
@blue.route('/project')
def project_home():
	projectdb_len = len(Project.query.filter_by(user_id=current_user.id).all())
	return render_template('project/project_home.html',title='Project',projectdb_len=projectdb_len)

#Project Add
@blue.route('/project/add',methods=['GET','POST'])
def project_add():
	form = NewProjectForm()
	if form.validate_on_submit():
		pass
	page = request.args.get('page',1,type=int)
	accesskey_list_len = len(AccessKey.query.filter_by(user_id=current_user.id).all())
	accesskey_list = AccessKey.query.filter_by(user_id=current_user.id).paginate(page=page,per_page=8)
	return render_template('project/project_add.html',title='Project Add',form=form,accesskey_list=accesskey_list,accesskey_list_len=accesskey_list_len)