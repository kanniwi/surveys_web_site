from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.repositories import UserRepository
from app import db
from datetime import datetime   

bp = Blueprint('main', __name__)

user_repository = UserRepository()

@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@bp.route('/update_profile', methods=['POST', 'GET'])
@login_required
def update_profile():    
    
    if request.method == 'POST':
        birth_date_str=request.form.get('birth_date')
        birth_date_res = datetime.strptime(birth_date_str, '%Y-%m-%d') if birth_date_str else None

        user_repository.update(
            user_id=current_user.id,
            username=request.form.get('username'),
            name=request.form.get('name'),
            surname=request.form.get('surname'),            
            birth_date=birth_date_res,
            email=request.form.get('email'),
            gender=request.form.get('gender')
        )
        flash('Профиль успешно обновлён', 'success')
        return redirect(url_for('main.profile'))


