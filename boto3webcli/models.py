from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from boto3webcli import app,db,login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	try:
		return User.query.get(int(user_id))
	except:
		return None


#User Data Model
class User(db.Model,UserMixin):
	__bind_key__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	firstname = db.Column(db.String(20),unique=True,nullable=False)		
	lastname = db.Column(db.String(20),unique=True,nullable=False)
	email = db.Column(db.String(120),unique=True,nullable=False)
	password = db.Column(db.String(60),nullable=False)
	confirm_email = db.Column(db.Boolean,default=False)
	mfa_enabled = db.Column(db.Boolean,default=False)
	mfa_key = db.Column(db.String(20),unique=True)
	image_file = db.Column(db.String(20),nullable=False,default='default_user.png')
	access_key = db.relationship('AccessKey',backref='user',lazy=True,cascade='all,delete-orphan')
	projects = db.relationship('Project',backref='user',lazy=True,cascade='all,delete-orphan')
	secgroup = db.relationship('SecurityGroup',backref='user',lazy=True,cascade='all,delete-orphan')

	def __repr__(self):
		return f"User('{self.firstname}','{self.email}')"

#Project DB Model
class Project(db.Model):
	__bind_key__ = 'project'
	id = db.Column(db.Integer,primary_key=True)
	projectname = db.Column(db.String(50),unique=True,nullable=False)
	project_region =  db.Column(db.String(10),nullable=False)
	accesskeyname = db.Column(db.String(20),unique=True,nullable=False)
	date_created = db.Column(db.DateTime(),nullable=False,default=datetime.now)
	accesskey_db = db.relationship('AccessKey',backref='project',uselist=False)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Project('{self.projectname}','{self.accesskey_db}','{self.user_id}')"

#AWS Access Key
class AccessKey(db.Model):
	__bind_key__ = 'accesskey'
	id = db.Column(db.Integer,primary_key=True)
	keyname = db.Column(db.String(20),unique=True,nullable=False)
	accesskeyid = db.Column(db.String(50),unique=True,nullable=False)
	secretkeyid = db.Column(db.String(50),unique=True,nullable=False)
	date_created = db.Column(db.DateTime(),nullable=False,default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	project_id = db.Column(db.Integer,db.ForeignKey('project.id'))
	
	def __repr__(self):
		return f"AccessKey('{self.keyname}','{self.accesskeyid}','{self.project_id}')"

#Security Group aka Firewall Rules
class SecurityGroup(db.Model):
	__bind_key__ = 'sg'
	id = db.Column(db.Integer,primary_key=True)
	sgname = db.Column(db.String(50))
	sgdescription= db.Column(db.String(200))
	vpcid = db.Column(db.String(50))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)