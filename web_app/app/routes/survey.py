from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository
from app.models import Survey, QuestionType, SurveyStatus, db
from datetime import datetime, timedelta

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

        # обновление сессии, чтобы получить айди нового опроса
        db.session.flush()


        form_data = request.form.to_dict(flat=False)

        questions_texts = form_data.get('questions[][text]', [])
        questions_types = form_data.get('questions[][type]', [])
        questions_required = form_data.get('questions[][required]', [])
        questions_answers = form_data.get('questions[][answers][]', [])

        answer_index = 0

        for i, question_text in enumerate(questions_texts):
            q_type = questions_types[i]
            is_required = i < len(questions_required)

            new_question = question_repository.create_question(
                survey_id=new_survey.id,
                question_text=question_text,
                question_type=QuestionType(q_type)
            )

            db.session.flush()

            if q_type in ['single', 'multiple']:
                while answer_index < len(questions_answers):
                    answer_text = questions_answers[answer_index]
                    if not answer_text.strip():
                        break
                    question_repository.add_option_to_question(
                        question_id=new_question.id,
                        option_text=answer_text
                    )
                    answer_index += 1

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

    for question in survey.questions:
        qid = question.id
        key = f"question_{qid}"

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

    flash("Ваши ответы успешно отправлены!", "success")
    return redirect(url_for("survey.catalog"))
