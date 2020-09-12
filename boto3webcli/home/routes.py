from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,mail,safe_seralizer,login_manager
from flask_login import login_user, current_user, logout_user, login_required
from boto3webcli.models import User
from boto3webcli.home.forms import UpdateAccountForm
import os
import secrets
from PIL import Image
import pyotp
import qrcode
import random
import string

#Blueprint object
blue = Blueprint('home',__name__,template_folder='templates')

#Home Page
@blue.route('/home')
def home():
	return render_template("home/home.html",title="Home")


#Function for Saving Profile Picture
def save_pictute(form_picture):
    renadom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = renadom_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/images/profile_pics',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

#User Profile
@blue.route('/user_profile',methods=['GET','POST'])
def user_profile():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_pictute(form.picture.data)
			current_user.image_file = picture_file

		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		current_user.password = hashed_password
		db.session.commit()
		return redirect(url_for('home.user_profile'))
	
	image_file = url_for('static',filename='images/profile_pics/' + current_user.image_file)
	return render_template("home/user_profile.html",title="User Profile",form=form,image_file=image_file)

#Function for generating QRCode for users MFA
def qrcode_generator(user_email_id):
	#Generating a base32 Secret Key
	mfa_key = pyotp.random_base32()
	qrcode_uri = pyotp.totp.TOTP(mfa_key).provisioning_uri(user_email_id,issuer_name="Boto3 Web Cli : MFA")

	#Generating QRCode
	qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
	)

	qr.add_data(qrcode_uri)
	qr.make(fit=True)
	qrimg = qr.make_image(fill_color="black", back_color="white")
	qrimg_save_path = os.path.join(app.root_path,'static/qr_code_img/')
	random_letter = string.ascii_letters
	qrcode_image_name = ''.join(current_user.email)
	qrimg.save(qrimg_save_path+qrcode_image_name+'.png')
	list_qrcode = []
	list_qrcode.insert(0,qrcode_image_name+'.png')
	list_qrcode.insert(1,mfa_key)
	return list_qrcode

#MFA
@blue.route('/mfa')
def mfa():
	if current_user.mfa_enabled != True:
		qrimg_name = qrcode_generator(current_user.email)
		return render_template('home/mfa.html',title='MFA',qrimg_name=qrimg_name[0],mfa_key=qrimg_name[1])
	else:
		return render_template('home/mfa.html',title="MFA")

#MFA Enabled and Logout
@blue.route('/home/mfa_enabled/<int:userid>/<string:mfa_key>')
def mfaenabled(userid,mfa_key):
	user = User.query.get(userid)
	user.mfa_key = mfa_key
	user.mfa_enabled = True
	db.session.commit()
	logout_user()
	flash('2-Step MultiFactor Authentication enabled for your account.','success')
	return redirect(url_for('user_management.login'))

#MFA Disabled and Logout
@blue.route('/home/mfa_disabled/<int:userid>')
def mfadisabled(userid):
	user = User.query.get(userid)
	user.mfa_enabled = False
	db.session.commit()
	logout_user()
	flash('2-Step MultiFactor Authentication disabled for your account.','success')
	return redirect(url_for('user_management.login'))
	
#User Logout
@blue.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user_management.login'))