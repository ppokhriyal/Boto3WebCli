from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager,mail,safe_seralizer
from boto3webcli.user_management.forms import LoginForm,RegisterForm,ForgotPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from boto3webcli.models import User
from flask_mail import Message
from itsdangerous.exc import SignatureExpired,BadTimeSignature

#Blueprint object
blue = Blueprint('user_management',__name__,template_folder='templates')


#Login
@blue.route('/')
def login():
	form = LoginForm()
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
	return render_template('user_management/message.html',msg=msg)


#Forgot Password
@blue.route('/forgot_password')
def forgot_password():
	form = ForgotPasswordForm()
	return render_template('user_management/forgot_password.html',title="Forgot Password",form=form)	

