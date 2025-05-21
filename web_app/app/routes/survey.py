from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories import survey_repository

bp = Blueprint('survey', __name__, url_prefix='/surveys')

@bp.route('/catalog')
def catalog():
    return render_template('survey/catalog.html')


@bp.route('/create', methods=['GET', 'POST'])
def create_survey():
    return render_template('survey/create.html')

@bp.route('/my_surveys')
@login_required
def my_surveys():
    surveys = survey_repository.get_surveys_by_user_id(current_user.id)
    return render_template('survey/my_surveys.html', surveys=surveys)

# редактирование общего описания опроса (название, даты и т.п.)
@bp.route('/<int:survey_id>/edit', methods=['GET', 'POST'])
def edit_survey(survey_id):
    return render_template('survey/edit', survey_id=survey_id)


# добавление/редактирование вопросов к опросу
@bp.route('/<int:survey_id>/edit-questions', methods=['GET'])
def edit_survey_questions(survey_id):
    pass

# Удаление опроса
@bp.route('/delete/<int:survey_id>', methods=['POST'])
def delete_survey(survey_id):
    pass

# Просмотр одного опроса (как участник)
@bp.route('/<int:survey_id>')
def view_survey(survey_id):
    pass

# Отправка ответов на опрос
@bp.route('/<int:survey_id>/submit', methods=['POST'])
def submit_survey(survey_id):
    pass