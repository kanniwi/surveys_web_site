from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories import SurveyRepository
from app.models import Survey

bp = Blueprint('survey', __name__, url_prefix='/surveys')

survey_repository = SurveyRepository()

@bp.route('/catalog')
def catalog():
    surveys = survey_repository.get_all_surveys()
    return render_template('survey/catalog.html', surveys=surveys)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':  
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
                 
        survey_repository.create_survey(title, description, current_user.id, start_date, end_date, 'active')
        flash('Опрос успешно создан', 'success')
        return redirect(url_for('survey.my_surveys'))

    if request.method == 'GET':
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
@bp.route('/<int:survey_id>/delete', methods=['POST'])
def delete_survey(survey_id):
    pass

@bp.route('/<int:survey_id>/take', methods=['POST'])
def take_survey(survey_id):
    return render_template('survey/take.html', survey_id=survey_id)

# Просмотр одного опроса (как участник)
@bp.route('/<int:survey_id>')
def view_survey(survey_id):
    pass

# Отправка ответов на опрос
@bp.route('/<int:survey_id>/submit', methods=['POST'])
def submit_survey(survey_id):
    pass