from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


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

#Forgot Password Form
class ForgotPasswordForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	submit = SubmitField('Reset Password')
