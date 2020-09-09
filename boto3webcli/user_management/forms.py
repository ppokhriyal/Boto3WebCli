from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from boto3webcli.models import User

#Login Form
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()],render_kw={'autofocus': True})
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#RegisterForm
class RegisterForm(FlaskForm):
	firstname = StringField('First Name',validators=[DataRequired(),Length(min=2,max=20)])
	lastname = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=20)])
	email = StringField('Email',validators=[DataRequired(),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password',message='Confirm Password must be matching Password')])
	submit = SubmitField('Create Account')

	def validate_firstname(self,firstname):
		user = User.query.filter_by(firstname=firstname.data).first()
		if user:
			raise ValidationError('This First Name is already taken. Please choose a diffrent one.')
	
	def validate_lastname(self,lastname):
		user = 	User.query.filter_by(lastname=lastname.data).first()
		if user:
			raise ValidationError('This Last Name is already taken. Please choose a diffrent one.')

	def validate_email(self,email):
		user = 	User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This email is already taken. Please choose a diffrent one.')

#Forgot Password Form
class ForgotPasswordForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	submit = SubmitField('Reset Password')

	def validate_email(self,email):
		user = 	User.query.filter_by(email=email.data).first()
		if not user:
			raise ValidationError('This email is not registered. Please choose the valid email id')

#Reset Password
class ResetPassword(FlaskForm):
	new_password = PasswordField('New Password',validators=[DataRequired()])
	confirm_new_password = PasswordField('Confirm New Password',validators=[DataRequired(),EqualTo('password',message='Confirm Password must be matching Password')])
	submit = SubmitField('Password Reset')


