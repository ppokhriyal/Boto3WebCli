from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from boto3webcli.models import User,AccessKey,Project


#Add New Project
class NewProjectForm(FlaskForm):
	projectname = StringField('Project Name',validators=[DataRequired(),Length(min=2,max=50)])
	access_keyname = StringField('Access Key Name',validators=[DataRequired(),Length(min=2,max=50)])
	submit = SubmitField('Create Project')

	def validate_projectname(self,projectname):
		
		if " " in projectname.data:
			raise ValidationError("Space not allowed.")
		
		projectname = Project.query.filter_by(projectname=projectname.data).first()
		if projectname:
			raise ValidationError('Project name already exists. Please choose a diffrent one.')

	def validate_access_keyname(self,access_keyname):
		if " " in access_keyname.data:
			raise ValidationError("Space not allowed.")
