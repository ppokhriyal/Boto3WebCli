from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from boto3webcli.user_management.forms import LoginForm,RegisterForm,ForgotPasswordForm,ResetPassword
from flask_login import login_user, current_user, logout_user, login_required
from boto3webcli.models import User
from flask_mail import Message
from itsdangerous.exc import SignatureExpired,BadTimeSignature
import os
import pyotp

#Blueprint object
blue = Blueprint('user_management',__name__,template_folder='templates')


#Login
@blue.route('/',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		#Check if email,password and confirm email is True
		if user and bcrypt.check_password_hash(user.password,form.password.data) and user.confirm_email == True:
			
			#Check if User has enabled MFA
			if user.mfa_enabled == True:
				return redirect(url_for('user_management.mfalogin',useremail=user.email,rem=form.remember.data))
			else:
				#If user has checked remember me
				login_user(user,remember=form.remember.data)
				next_page = request.args.get('next')
				return redirect(next_page) if next_page else redirect(url_for('home.home'))
		else:
			flash('Login Unsuccessful. Please check email or password or your email id is not yet confirmed.','danger')	
	return render_template('user_management/login.html',title="Login",form=form)


#Register
@blue.route('/register',methods=['GET','POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		#Create database for new user
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(firstname=form.firstname.data,lastname=form.lastname.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		
		#Generate Account Creation confirmation mail
		email = form.email.data
		token = safe_seralizer.dumps(email,salt='email-confirm')
		msg = Message('Boto3 Web Cli : Account creation confirmation',sender='ppokhriyal4@gmail.com',recipients=[email])
		link = url_for('user_management.confirm_email',token=token,user_id=user.id,_external=True)
		msg.body= 'Please navigate to below link, for your account confirmation \n\n {}'.format(link)
		mail.send(msg)
		
		return redirect(url_for('user_management.message',msg='mail_sent'))

	return render_template('user_management/register.html',title="Register",form=form)

#Mail session
@blue.route('/confirm_email/<token>/<int:user_id>')
def confirm_email(token,user_id):
	try:
		email = safe_seralizer.loads(token,salt='email-confirm',max_age=3600)
	except SignatureExpired:
		return redirect(url_for('user_management.message',msg='mail_expired'))
	except BadTimeSignature:
		return redirect(url_for('user_management.message',msg='mail_linkerror'))

	#Confirm user email verification
	user = User.query.get(user_id)
	email_confirm_status = user.confirm_email

	if email_confirm_status == True:
		flash('Your Account is already created.Plase Login!','info')
		return redirect(url_for('user_management.login'))
	else:
		user.confirm_email = True
		db.session.commit()
		flash('Your Account created successfully.Plase Login!','success')
		return redirect(url_for('user_management.login'))	

#Message
@blue.route('/message/<msg>')
def message(msg):
	return render_template('user_management/message.html',title="Message",msg=msg)


#Forgot Password
@blue.route('/forgot_password',methods=['POST','GET'])
def forgot_password():
	form = ForgotPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		#Generate Password reset link mail
		email = form.email.data
		token = safe_seralizer.dumps(email,salt='email-confirm')
		msg = Message('Boto3 Web Cli : Password Reset',sender='ppokhriyal4@gmail.com',recipients=[email])
		link = url_for('user_management.password_reset_email',token=token,user_id=user.id,_external=True)
		msg.body= 'Please navigate to below link, for your password reset \n\n {}'.format(link)
		mail.send(msg)
		
		return redirect(url_for('user_management.message',msg='password_reset_mail_sent'))

	return render_template('user_management/forgot_password.html',title="Forgot Password",form=form)	

#Password Reset Mail
@blue.route('/password_reset_email/<token>/<int:user_id>')
def password_reset_email(token,user_id):
	try:
		email = safe_seralizer.loads(token,salt='email-confirm',max_age=3600)
	except SignatureExpired:
		return redirect(url_for('user_management.message',msg='mail_expired'))
	except BadTimeSignature:
		return redirect(url_for('user_management.message',msg='mail_linkerror'))

	form = ResetPassword()
	return render_template('user_management/reset_password.html',title="Reset Password",form=form,userid=user_id)

#Reset Password
@blue.route('/reset_password/<int:userid>',methods=['POST','GET'])
def reset_password(userid):
	form = ResetPassword()
	user = User.query.get_or_404(userid)
	if request.method == 'POST':
		hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash("Your new password has ben set successfully",'success')
		return redirect(url_for('user_management.login'))

#MFA Login
@blue.route('/mfalogin/<string:useremail>/<string:rem>',methods=['POST','GET'])
def mfalogin(useremail,rem):
	user = User.query.filter_by(email=useremail).first()
	return render_template('user_management/mfa_authentication.html',title='MFA Login',user=user,rem=rem)

#MFA Authentication
@blue.route('/mfa/authentication/<string:useremail>/<string:mfakey>/<string:rem>',methods=['POST','GET'])
def mfa_authentication(useremail,mfakey,rem):
	user = User.query.filter_by(email=useremail).first()
	totp = pyotp.TOTP(mfakey)
	#Verify OTP
	if totp.now() == request.form['verificationcode']:
		login_user(user,remember=rem)
		next_page = request.args.get('next')
		return redirect(next_page) if next_page else redirect(url_for('home.home'))
	else:
		flash('Login Unsuccessful.Please check the Verification code','danger')
		return redirect(url_for('user_management.login'))
