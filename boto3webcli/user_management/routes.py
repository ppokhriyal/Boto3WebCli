from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app,db,bcrypt,login_manager
from boto3webcli.user_management.forms import LoginForm,RegisterForm,ForgotPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from boto3webcli.models import User

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
		
		flash("Account created successfully",'success')
		return redirect(url_for('user_management.login'))

	return render_template('user_management/register.html',title="Register",form=form)

#Forgot Password
@blue.route('/forgot_password')
def forgot_password():
	form = ForgotPasswordForm()
	return render_template('user_management/forgot_password.html',title="Forgot Password",form=form)	

