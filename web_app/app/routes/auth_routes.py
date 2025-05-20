from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User
from repositories import UserRepository
from utils.helpers import password_strength 

user_repository = UserRepository()

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Авторизуйте для доступа к этому ресурсу'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')   
        remember_me = request.form.get('remember_me', None) == 'on'
        
        user = user_repository.get_user_by_username_and_password(username, password)
        
        if user:
            flash('Авторизаия прошла успешно', 'success')
            login_user(user, remember=remember_me)
            return redirect(url_for('main.index'))
        
        flash('Неверное имя пользователя или пароль', 'danger')
        return render_template('auth/login.html')
        
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('main.index'))     

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if email and username and password and password_confirm:
            if user_repository.exists_by_username(username):
                flash('Пользователь с таким именем уже существует', 'danger')
                return render_template('auth/register.html')
            if password != password_confirm:
                flash('Пароли не совпадают', 'danger')
                return render_template('auth/register.html')
            if not password_strength(password):
                flash('Пароль должен быть не менее 8 символов, содержать заглавные, строчные буквы и цифры')
                return render_template('auth/register.html')
                
            user_repository.create(username, email, password, 'user') 
            flash('Регистрация прошла успешно', 'success')
            return redirect(url_for('auth.login'))     
        
    flash('Заполните все поля','danger')
    render_template('auth/register.html')
    

        
        


        
        