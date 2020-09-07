from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app
from boto3webcli.user_management.forms import LoginForm,RegisterForm,ForgotPasswordForm

#Blueprint object

blue = Blueprint('user_management',__name__,template_folder='templates')


#Login
@blue.route('/')
def login():
	form = LoginForm()
	return render_template('user_management/login.html',title="Login",form=form)


#Register
@blue.route('/register')
def register():
	form = RegisterForm()
	return render_template('user_management/register.html',title="Register",form=form)

#Forgot Password
@blue.route('/forgot_password')
def forgot_password():
	form = ForgotPasswordForm()
	return render_template('user_management/forgot_password.html',title="Forgot Password",form=form)	

