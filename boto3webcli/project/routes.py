from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.project.forms import NewProjectForm
from boto3webcli.models import User,Project,AccessKey,SecurityGroup
import botocore
import boto3
import json

#Blueprint object
blue = Blueprint('project',__name__,template_folder='templates')


#Project Home
@blue.route('/project')
@fresh_login_required
def project_home():
	page = request.args.get('page',1,type=int)
	projectdb_len = len(Project.query.filter_by(user_id=current_user.id).all())
	project_record = Project.query.filter_by(user=current_user).paginate(page=page,per_page=10)
	return render_template('project/project_home.html',title='Project',projectdb_len=projectdb_len,project_record=project_record)

#Project Add
@blue.route('/project/add',methods=['GET','POST'])
@fresh_login_required
def project_add():
	form = NewProjectForm()
	page = request.args.get('page',1,type=int)
	accesskey_list_len = len(AccessKey.query.filter_by(user_id=current_user.id).all())
	accesskey_list = AccessKey.query.filter_by(user_id=current_user.id).paginate(page=page,per_page=8)

	if form.validate_on_submit():
		
		#Add new project
		project_db = Project(projectname=form.projectname.data,accesskeyname=form.access_keyname.data,project_region=form.awsregion.data,user=current_user)
		db.session.add(project_db)
		db.session.commit()
		
		#Update Access Key DB with new Project id
		project_db = db.session.query(Project).filter(Project.projectname==form.projectname.data).first()
		accesskey_db = db.session.query(AccessKey).filter(AccessKey.keyname==form.access_keyname.data).first()
		accesskey_db.project_id = project_db.id
		db.session.commit()

		return redirect(url_for('project.project_home'))
	
	return render_template('project/project_add.html',title='Project Add',form=form,accesskey_list=accesskey_list,accesskey_list_len=accesskey_list_len)

#Function for Instance Types
def instance_types():
	accesskey = db.session.query(AccessKey).filter(AccessKey.user_id==current_user.id).first()
	client_ec2 = boto3.client('ec2',region_name='us-west-2',aws_access_key_id=accesskey.accesskeyid,aws_secret_access_key=accesskey.secretkeyid)
	instance = client_ec2.describe_instance_types(InstanceTypes=['t1.micro','t2.nano','t2.micro','t2.small','t2.medium','t2.large','t2.xlarge','t2.2xlarge',
		't3.nano','t3.micro','t3.small','t3.medium','t3.large','t3.xlarge','t3.2xlarge','t3a.nano','t3a.micro',
		't3a.small','t3a.medium','t3a.large','t3a.xlarge','t3a.2xlarge','t4g.nano','t4g.micro','t4g.small',
		't4g.medium','t4g.large','t4g.xlarge','m1.small','m1.medium','m1.large','m1.xlarge','m3.medium','m3.large'])

	return instance

#EC2 Build
@blue.route('/project/build/ec2')
@fresh_login_required
def ec2_build():
	instance_type = instance_types()
	return render_template('project/ec2_build.html',title="EC2 Build",instance_type=instance_type)