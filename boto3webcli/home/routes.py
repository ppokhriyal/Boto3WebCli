from flask import Blueprint,render_template,url_for, flash, redirect, request, abort, session
from flask_login import login_user, current_user, logout_user, login_required

#Blueprint object
blue = Blueprint('home',__name__,template_folder='templates')

#Home Page
@blue.route('/home')
def home():
	return render_template("home/home.html")



#User Logout
@blue.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user_management.login'))