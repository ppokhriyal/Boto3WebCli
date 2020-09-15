from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session,jsonify
from boto3webcli import app,db,bcrypt,mail,safe_seralizer,login_manager
from flask_login import login_user, current_user, logout_user, login_required,fresh_login_required
from boto3webcli.awsaccesskey.forms import AccessKeyForm
from boto3webcli.models import User,AccessKey,Project
import botocore
import boto3
import json

#Blueprint object
blue = Blueprint('awsaccesskey',__name__,template_folder='templates')

#AWS Access Key Home
@blue.route('/awsaccesskey')
@fresh_login_required
def awsaccesskey_home():
	page = request.args.get('page',1,type=int)
	accesskeydb_len = len(AccessKey.query.filter_by(user_id=current_user.id).all())
	accesskey_record = AccessKey.query.filter_by(user=current_user).paginate(page=page,per_page=10)
	return render_template('awsaccesskey/awsaccesskey_home.html',title="Access Key",accesskeydb_len=accesskeydb_len,accesskey_record=accesskey_record)

#Access Key Add
@blue.route('/awsaccesskey/add',methods=['GET','POST'])
@fresh_login_required
def awsaccesskey_add():
	form = AccessKeyForm()
	if form.validate_on_submit():
		accesskey_db = AccessKey(keyname=form.keyname.data,accesskeyid=form.access_keyid.data,secretkeyid=form.secret_keyid.data,user=current_user)
		db.session.add(accesskey_db)
		db.session.commit()
		return redirect(url_for('awsaccesskey.awsaccesskey_home'))
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

#Remove AWS Access Key
@blue.route('/awsaccesskey/remove/<int:accessid>',methods=['POST','GET'])
@fresh_login_required
def awsaccesskey_remove(accessid):
	access_id = AccessKey.query.get_or_404(accessid)

	db.session.delete(access_id)
	db.session.commit()
	return redirect(url_for('awsaccesskey.awsaccesskey_home'))


