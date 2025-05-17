from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Авторизуйте для доступа к этому ресурсу'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bp.route('/login', methods=['GET', 'POST']):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')   
        remember_me = request.form.get('remember_me')
        