from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session, jsonify
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.project.forms import NewProjectForm,Firewall_SG_Form
from boto3webcli.models import User,Project,AccessKey,SecurityGroup,Vpc
import botocore
import boto3
import json
import urllib3

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

		#Add VPC Info
		accesskey = db.session.query(AccessKey).filter(AccessKey.user_id==current_user.id).first()
		project = db.session.query(Project).filter(Project.user_id==current_user.id).first()
		client = boto3.client('ec2',region_name=project.project_region,aws_access_key_id=accesskey.accesskeyid,aws_secret_access_key=accesskey.secretkeyid)
		vpc_response = client.describe_vpcs()
		vpc = Vpc(vpcid=vpc_response['Vpcs'][0]['VpcId'],ownerid=vpc_response['Vpcs'][0]['OwnerId'],vpc_state=vpc_response['Vpcs'][0]['State'],cidrblock=vpc_response['Vpcs'][0]['CidrBlock'],user=current_user,project=project)
		db.session.add(vpc)
		db.session.commit()
		
		
		return redirect(url_for('project.project_home'))
	
	return render_template('project/project_add.html',title='Project Add',form=form,accesskey_list=accesskey_list,accesskey_list_len=accesskey_list_len)

#Project Dashboard
@blue.route('/project/dashboard')
def project_dashboard():
	project = db.session.query(Project).filter(Project.user_id==current_user.id).first()

	return render_template('project/project_dashboard.html',title='Project Dashboard',project=project)

#Function for Instance Types
def instance_types():
	accesskey = db.session.query(AccessKey).filter(AccessKey.user_id==current_user.id).first()
	project = db.session.query(Project).filter(Project.user_id==current_user.id).first()

	client_ec2 = boto3.client('ec2',region_name=project.project_region,aws_access_key_id=accesskey.accesskeyid,aws_secret_access_key=accesskey.secretkeyid)
	instance = client_ec2.describe_instance_types()

	return instance

#EC2 Build
@blue.route('/project/build/ec2')
@fresh_login_required
def ec2_build():
	instance_type = instance_types()
	project = db.session.query(Project).filter(Project.user_id==current_user.id).first()
	return render_template('project/ec2_build.html',title="EC2 Build",instance_type=instance_type,project=project)

#Get My Ip
@blue.route('/project/getmyip',methods=['GET','POST'])
def myip():
	https = urllib3.PoolManager()
	r = https.request('GET',"https://api.ipify.org/?/format=jason")
	if r.status != 200:
		return jsonify({'result':'fail'})
	else:
		ip = r.data.decode('utf-8')
		return jsonify({'result': ip})

#Firewall Rule Create
@blue.route('/project/firewall',methods=['GET','POST'])
@fresh_login_required
def firewall_rule_create():
	form = Firewall_SG_Form()
	project = db.session.query(Project).filter(Project.user_id==current_user.id).first()

	if form.validate_on_submit():

		#Check if any rule is added or not
		rulebook_check = request.form.getlist('rulebooklist')
		
		if len(rulebook_check) == 0:
			flash(f'Rules are not added.Please add rules to your SecurityGroup','danger')

		#Create SG
		accesskey = db.session.query(AccessKey).filter(AccessKey.user_id==current_user.id).first()
		project = db.session.query(Project).filter(Project.user_id==current_user.id).first()
		client_ec2 = boto3.client('ec2',region_name=project.project_region,aws_access_key_id=accesskey.accesskeyid,aws_secret_access_key=accesskey.secretkeyid)

		#breakdown rulebook list
		rule = rulebook_check[0].split(',')

		security_group_response = client_ec2.create_security_group(Description=rule[0],
			GroupName=rule[1],
			VpcId=form.vpc.data)

		security_group_id = security_group_response['GroupId']

		sg_policy = client_ec2.authorize_security_group_ingress(
			GroupId=security_group_id,
			Description=rulebook_check[3],
			IpPermissions=[
			{'IpProtocol': rulebook_check[0],
			'FormPort': rulebook_check[1],
			'ToPort': rulebook_check[1],
			'IpRanges' : [{'CidrIp' : rulebook_check[2]}]}])
		

	return render_template('project/firewall_create.html',title="Firewall Rules",project=project,form=form)
