from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session,jsonify
from boto3webcli import app,db,bcrypt,mail,safe_seralizer,login_manager
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.awsaccesskey.forms import AccessKeyForm
from boto3webcli.models import User,AccessKey
import botocore
import boto3
import json

#Blueprint object
blue = Blueprint('awsaccesskey',__name__,template_folder='templates')

#AWS Access Key Home
@blue.route('/awsaccesskey')
@fresh_login_required
def awsaccesskey_home():
	accesskeydb_len = len(AccessKey.query.filter_by(user_id=current_user.id).all())
	return render_template('awsaccesskey/awsaccesskey_home.html',title="Access Key",accesskeydb_len=accesskeydb_len)

#Access Key Add
@blue.route('/awsaccesskey/add')
@fresh_login_required
def awsaccesskey_add():
	form = AccessKeyForm()
	return render_template('awsaccesskey/awsaccesskey_add.html',title="Add Access Key",form=form)

#Verify Acess Key Id
@blue.route('/awsaccesskey/verify_key/<string:accesskey>/<string:secretkey>',methods=['GET','POST'])
@fresh_login_required
def verify_key(accesskey,secretkey):
	sts = boto3.client('sts',aws_access_key_id=accesskey,aws_secret_access_key=secretkey)
	try:
		sts.get_caller_identity()
		return jsonify({'result':'pass'})
	except botocore.exceptions.ClientError:
		return jsonify({'result':'fail'})



