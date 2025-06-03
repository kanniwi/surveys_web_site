from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository
from app.models import Survey, QuestionType, SurveyStatus, db
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from app.utils.helpers import check_not_blocked, survey_active_required
from datetime import timezone
from math import ceil


bp = Blueprint('survey', __name__, url_prefix='/surveys')

survey_repository = SurveyRepository()
question_repository = QuestionRepository()
user_response_repository = UserResponseRepository()

@bp.route('/catalog')
def catalog():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest') 
    per_page = 20

    all_surveys = survey_repository.get_surveys_with_counts()

    if sort == 'responses':
        all_surveys.sort(key=lambda x: x['response_count'], reverse=True)
    else:  
        all_surveys.sort(key=lambda x: x['survey'].start_date, reverse=True)

    total = len(all_surveys)
    total_pages = ceil(total / per_page)

    surveys_paginated = all_surveys[(page - 1) * per_page : page * per_page]

    return render_template(
        'survey/catalog.html',
        surveys=surveys_paginated,
        page=page,
        total_pages=total_pages,
        sort=sort 
    )


@bp.route('/my_surveys')
@login_required
def my_surveys():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    sort = request.args.get('sort', 'newest') 
    surveys_with_counts = survey_repository.get_surveys_with_counts(user_id=current_user.id)
    
    if sort == 'responses':
        surveys_with_counts.sort(key=lambda x: x['response_count'], reverse=True)
    else:  
        surveys_with_counts.sort(key=lambda x: x['survey'].start_date, reverse=True)
    
    total = len(surveys_with_counts)
    surveys_paginated = surveys_with_counts[(page - 1) * per_page : page * per_page]
    total_pages = ceil(total / per_page)
    return render_template(
        'survey/my_surveys.html',
        surveys=surveys_paginated,
        page=page,
        total_pages=total_pages
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_not_blocked
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        else:
            start_date = datetime.now(timezone.utc)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        else:
            end_date = datetime(2999, 12, 31, tzinfo=timezone.utc)
            
        print("start_date:", start_date)
        print("end_date:", end_date)
        print("now:", datetime.now(timezone.utc))

        new_survey = survey_repository.create_survey(
            title=title,
            description=description,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            status=SurveyStatus.active
        )

        db.session.flush()

        form_data = request.form.to_dict(flat=False)
        files = request.files.to_dict(flat=False)

        question_indices = set()
        for key in form_data.keys():
            if key.startswith('questions[') and '][text]' in key:
                index = key.split('[')[1].split(']')[0]
                question_indices.add(int(index))

        for index in sorted(question_indices):
            question_text = form_data.get(f'questions[{index}][text]', [''])[0]
            question_type = form_data.get(f'questions[{index}][type]', ['single'])[0]
            is_required = f'questions[{index}][required]' in form_data

            image_path = None
            if f'questions[{index}][image]' in files:
                image_file = files[f'questions[{index}][image]'][0]
                if image_file and image_file.filename:

                    filename = secure_filename(image_file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    image_path = f"uploads/questions/{unique_filename}"
                    
                    image_file.save(os.path.join('app', image_path))

            new_question = question_repository.create_question(
                survey_id=new_survey.id,
                question_text=question_text,
                question_type=QuestionType(question_type),
                required=is_required,
                image_path=image_path
            )

            db.session.flush()

            if question_type in ['single', 'multiple']:
                answer_key = f'questions[{index}][answers][]'
                if answer_key in form_data:
                    for answer_text in form_data[answer_key]:
                        if answer_text.strip():
                            question_repository.add_option_to_question(
                                question_id=new_question.id,
                                option_text=answer_text
                            )

        db.session.commit()
        flash("Опрос успешно создан!", "success")
        return redirect(url_for("survey.my_surveys"))

    return render_template("survey/create.html")


@bp.route('/<int:survey_id>/take', methods=['GET', 'POST'])
@survey_active_required
def take_survey(survey, survey_id):
    if current_user.is_authenticated:
        existing_responses = user_response_repository.get_user_responses_for_survey(
            user_id=current_user.id,
            survey_id=survey_id
        )
        if existing_responses:
            flash("Вы уже проходили этот опрос.", "warning")
            return redirect(url_for("survey.catalog"))
    
    return render_template('survey/take.html', survey=survey)


@bp.route('/<int:survey_id>/submit', methods=['POST'])
@login_required
def submit_survey(survey_id):
    survey_repo = SurveyRepository()
    user_response_repo = UserResponseRepository()

    survey = survey_repo.get_survey_by_id(survey_id)
    if not survey:
        flash("Опрос не найден.", "danger")
        return redirect(url_for("survey.catalog"))

    form_data = request.form
    errors = []

    for question in survey.questions:
        qid = question.id
        key = f"question_{qid}"

        if question.required:
            if question.question_type.value == "text":
                answer = form_data.get(key)
                if not answer or not answer.strip():
                    errors.append(f"Вопрос '{question.question_text}' требует ответа")
                    continue

            elif question.question_type.value == "single":
                option_id = form_data.get(key)
                if not option_id:
                    errors.append(f"Вопрос '{question.question_text}' требует ответа")
                    continue

            elif question.question_type.value == "multiple":
                option_ids = form_data.getlist(key + "[]")
                if not option_ids:
                    errors.append(f"Вопрос '{question.question_text}' требует ответа")
                    continue

        if question.question_type.value == "text":
            answer = form_data.get(key)
            if answer:
                user_response_repo.save_response(
                    user_id=current_user.id,
                    survey_id=survey_id,
                    question_id=qid,
                    text_answer=answer
                )

        elif question.question_type.value == "single":
            option_id = form_data.get(key)
            if option_id:
                user_response_repo.save_response(
                    user_id=current_user.id,
                    survey_id=survey_id,
                    question_id=qid,
                    option_id=int(option_id)
                )

        elif question.question_type.value == "multiple":
            option_ids = form_data.getlist(key + "[]")
            for opt_id in option_ids:
                user_response_repo.save_response(
                    user_id=current_user.id,
                    survey_id=survey_id,
                    question_id=qid,
                    option_id=int(opt_id)
                )

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("survey.take_survey", survey_id=survey_id))

    flash("Ваши ответы успешно отправлены!", "success")
    return redirect(url_for("survey.catalog"))
