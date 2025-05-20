from flask import Blueprint
from flask_login import login_required

bp = Blueprint('stats', __name__, url_prefix='/stats')

# Общая статистика по всем опросам (например, сколько пройдено, активных и т.п.)
@bp.route('/')
@login_required
def overall_stats():
    pass

# Статистика по конкретному опросу: сколько людей прошли, распределение ответов
@bp.route('/survey/<int:survey_id>')
@login_required
def survey_stats(survey_id):
    pass

# Подробная статистика по конкретному вопросу внутри опроса
@bp.route('/question/<int:question_id>')
@login_required
def question_stats(question_id):
    pass

# Статистика по пользователям: кто сколько прошёл, какие результаты
@bp.route('/users')
@login_required
def user_stats():
    pass

# Результаты конкретного пользователя
@bp.route('/user/<int:user_id>')
@login_required
def single_user_stats(user_id):
    pass
