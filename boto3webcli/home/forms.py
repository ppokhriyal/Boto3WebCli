from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from boto3webcli.models import User



class UpdateAccountForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password',message='Confirm Password must be matching Password')])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpeg','png'])])
    submit = SubmitField('Save changes')    