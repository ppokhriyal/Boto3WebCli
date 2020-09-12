from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from boto3webcli.models import User,AccessKey


#Access Key Form
class AccessKeyForm(FlaskForm):
	keyname = StringField('Key Name',validators=[DataRequired(),Length(min=2,max=50)])
	access_keyid = StringField('Access Key Id',validators=[DataRequired(),Length(min=2,max=50)])
	secret_keyid = PasswordField('Secret Key Id',validators=[DataRequired(),Length(min=2,max=50)])
	submit = SubmitField('Add Key')

	