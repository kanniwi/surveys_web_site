import re
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import Survey

def password_strength(password):
    if re.match(r'^(?=.*\d)(?=.*[A-ZА-ЯЁ])(?=.*[a-zа-яё])[^ ]{8,128}$', password):
        return True
    return False

def check_not_blocked(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_blocked:
            flash('Ваш аккаунт заблокирован. Действие недоступно.', 'danger')
            return redirect(url_for('main.index'))
        return view_func(*args, **kwargs)
    return wrapper

def survey_active_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        survey_id = kwargs.get('survey_id')
        survey = Survey.query.get(survey_id)
        if not survey:
            flash('Опрос не найден.', 'warning')
            return redirect(url_for('main.index'))
        if not survey.is_active():
            flash('Опрос завершён или ещё не начался. Доступна только статистика.', 'info')
            return redirect(url_for('stats.survey_stats', survey_id=survey_id))
        return view_func(survey=survey, *args, **kwargs)
    
    return wrapped_view

