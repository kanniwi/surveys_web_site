from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository
from app.models import Survey, QuestionType, SurveyStatus, db
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename


bp = Blueprint('survey', __name__, url_prefix='/surveys')

survey_repository = SurveyRepository()
question_repository = QuestionRepository()
user_response_repository = UserResponseRepository()

@bp.route('/catalog')
def catalog():
    surveys_with_counts = survey_repository.get_surveys_with_counts()
    return render_template('survey/catalog.html', surveys=surveys_with_counts)

@bp.route('/my_surveys')
@login_required
def my_surveys():
    surveys_with_counts = survey_repository.get_surveys_with_counts(user_id=current_user.id)
    return render_template('survey/my_surveys.html', surveys=surveys_with_counts)



@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=365)

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

        # Get all question indices from the form data
        question_indices = set()
        for key in form_data.keys():
            if key.startswith('questions[') and '][text]' in key:
                index = key.split('[')[1].split(']')[0]
                question_indices.add(int(index))

        # Process questions in order
        for index in sorted(question_indices):
            question_text = form_data.get(f'questions[{index}][text]', [''])[0]
            question_type = form_data.get(f'questions[{index}][type]', ['single'])[0]
            is_required = f'questions[{index}][required]' in form_data

            # Handle image upload
            image_path = None
            if f'questions[{index}][image]' in files:
                image_file = files[f'questions[{index}][image]'][0]
                if image_file and image_file.filename:
                    # Generate unique filename
                    filename = secure_filename(image_file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    image_path = f"uploads/questions/{unique_filename}"
                    
                    # Save the file
                    image_file.save(os.path.join('app/static', image_path))

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



@bp.route('/<int:survey_id>/edit', methods=['GET', 'POST'])
def edit_survey(survey_id):
    return render_template('survey/edit', survey_id=survey_id)


@bp.route('/<int:survey_id>/edit-questions', methods=['GET'])
def edit_survey_questions(survey_id):
    pass


@bp.route('/<int:survey_id>/delete', methods=['POST'])
def delete_survey(survey_id):
    pass

@bp.route('/<int:survey_id>/take', methods=['GET', 'POST'])
def take_survey(survey_id):
    survey = survey_repository.get_survey_by_id(survey_id=survey_id)
    return render_template('survey/take.html', survey=survey)


@bp.route('/<int:survey_id>')
def view_survey(survey_id):
    pass


@bp.route('/<int:survey_id>/submit', methods=['POST'])
@login_required
def submit_survey(survey_id):
    from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository
    survey_repo = SurveyRepository()
    question_repo = QuestionRepository()
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

        # Проверяем обязательные вопросы
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

        # Сохраняем ответы
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
