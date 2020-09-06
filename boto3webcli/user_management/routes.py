from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from boto3webcli import app


#Blueprint object

blue = Blueprint('user_management',__name__,template_folder='templates')


#Login
@blue.route('/')
def login():
	return render_template('user_management/login.html',title="Login")


#Register
@blue.route('/register')
def register():
	return render_template('user_management/register.html',title="Register")

#Forgot Password
@blue.route('/forgot_password')
def forgot_password():
	return render_template('user_management/forgot_password.html',title="Forgot Password")	

