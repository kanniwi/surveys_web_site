from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.repositories import UserRepository, SurveyRepository
from app import db
from datetime import datetime   

bp = Blueprint('main', __name__)

user_repository = UserRepository()

survey_repository = SurveyRepository()

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
            name=request.form.get('name'),
            surname=request.form.get('surname'),            
            birth_date=birth_date_res,
            gender=request.form.get('gender')
        )
        flash('Профиль успешно обновлён', 'success')
        return redirect(url_for('main.profile'))
    flash('Ошибка обновления профиля', 'danger')
    return redirect(url_for('main.profile'))


@bp.route('/admin_users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role.value != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'danger')
        return redirect(url_for('main.index'))

    users = user_repository.all()
    return render_template('main/users.html', users=users)

@bp.route('/admin_surveys', methods=['GET', 'POST'])
@login_required
def admin_surveys():
    if current_user.role.value != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'danger')
        return redirect(url_for('main.index'))
    
    surveys = survey_repository.all()
    return render_template('main/surveys.html', surveys=surveys)
    
    
@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role.value != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('main.admin_users'))

    user_repository.delete(user_id)
    flash('Пользователь удалён', 'success')
    return redirect(url_for('main.admin_users'))


@bp.route('/users/<int:user_id>/toggle_block', methods=['POST'])
@login_required
def toggle_block_user(user_id):
    if current_user.role.value != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('main.admin_users'))

    user = user_repository.get_user_by_id(user_id)
    if not user:
        flash('Пользователь не найден', 'warning')
        return redirect(url_for('main.admin_users'))

    is_blocked = not user.is_blocked
    user_repository.update(user_id=user.id, is_blocked=is_blocked)
    flash('Статус пользователя обновлён', 'info')
    return redirect(url_for('main.admin_users'))


