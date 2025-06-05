from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, send_file
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

# Добавляем маршрут для обработки загруженных файлов
@bp.route('/uploads/<path:filename>')
def uploads(filename):
    print(f"\n=== Uploads Route Debug ===")
    print(f"Received filename: {filename}")
    
    # Если путь начинается с 'uploads/', убираем этот префикс
    if filename.startswith('uploads/'):
        filename = filename[8:]  # Убираем 'uploads/'
        print(f"Removed 'uploads/' prefix. New filename: {filename}")
    
    # Разбиваем путь на части
    parts = filename.split('/')
    if len(parts) > 1:
        # Если есть поддиректории, используем их
        directory = os.path.join('app', 'uploads', *parts[:-1])
        filename = parts[-1]
    else:
        # Если это файл в корневой директории
        directory = os.path.join('app', 'uploads')
        filename = parts[0]
    
    # Преобразуем все пути в формат с прямыми слешами
    directory = directory.replace('\\', '/')
    full_path = f"{directory}/{filename}"
    
    # Проверяем существование директории и файла
    print(f"Directory: {directory}")
    print(f"Filename: {filename}")
    print(f"Directory exists: {os.path.exists(directory)}")
    print(f"Full path: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")
    
    try:
        return send_file(full_path)
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return "File not found", 404

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
    current_utc_time = datetime.now(timezone.utc)

    for entry in surveys_with_counts:
        survey = entry['survey']
        if survey.start_date.tzinfo is None:
            survey.start_date = survey.start_date.replace(tzinfo=timezone.utc)

    return render_template(
        'survey/my_surveys.html',
        surveys=surveys_paginated,
        page=page,
        total_pages=total_pages,
        sort=sort,
        current_time=current_utc_time
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
                    image_path = f"questions/{unique_filename}"
                    
                    # Создаем директорию, если она не существует
                    upload_dir = os.path.join('app', 'uploads', 'questions')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Сохраняем файл
                    save_path = os.path.join('app', 'uploads', image_path)
                    image_file.save(save_path)
                    print(f"  New image saved: {image_path}")
            else:
                # Если новое изображение не загружено, используем существующее
                old_question = old_questions[index] if index < len(old_questions) else None
                if old_question and old_question.id in existing_images:
                    image_path = existing_images[old_question.id]
                    print(f"  Using existing image: {image_path}")

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

from datetime import datetime, timezone

@bp.route('/<int:survey_id>/edit', methods=['GET', 'POST'])
@login_required
@check_not_blocked
def edit_survey(survey_id):
    survey = survey_repository.get_survey_by_id(survey_id)

    if not survey:
        flash("Опрос не найден", "danger")
        return redirect(url_for('main.index'))

    if survey.user_id != current_user.id and current_user.role != 'admin':
        flash("У вас нет прав для редактирования этого опроса", "danger")
        return redirect(url_for('main.index'))

    if survey.start_date:
        if survey.start_date.tzinfo is None:
            survey_start = survey.start_date.replace(tzinfo=timezone.utc)
        else:
            survey_start = survey.start_date

        if survey_start <= datetime.now(timezone.utc):
            flash("Редактирование запрещено — опрос уже начался", "warning")
            return redirect(url_for('stats.survey_stats', survey_id=survey.id))

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict(flat=False)
            files = request.files.to_dict(flat=False)

            print("=== Form Data Debug ===")
            print("All form data:", form_data)
            print("All files:", files)

            # Обновляем основную информацию об опросе
            survey.title = request.form.get('title')
            survey.description = request.form.get('description')

            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')

            survey.start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc) if start_date_str else datetime.now(timezone.utc)
            survey.end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc) if end_date_str else datetime(2999, 12, 31, tzinfo=timezone.utc)

            # Создаем словарь для хранения существующих изображений
            existing_images = {q.id: q.image_path for q in survey.questions}
            print("Existing images:", existing_images)

            # Сначала удаляем старые вопросы
            print("\nDeleting old questions:")
            old_questions = list(survey.questions)
            for q in old_questions:
                print(f"  Deleting question {q.id}")
                question_repository.delete_question(q.id)

            # Создаем новые вопросы
            new_questions = []
            question_indices = set()
            
            # Собираем все индексы вопросов из формы
            for key in form_data.keys():
                if key.startswith('questions[') and '][text]' in key:
                    try:
                        index = int(key.split('[')[1].split(']')[0])
                        question_indices.add(index)
                        print(f"Found question index: {index} in key: {key}")
                    except ValueError:
                        print(f"Invalid question index in key: {key}")
                        continue

            print("Question indices:", sorted(question_indices))

            # Создаем новые вопросы
            for index in sorted(question_indices):
                question_text = form_data.get(f'questions[{index}][text]', [''])[0]
                question_type = form_data.get(f'questions[{index}][type]', ['single'])[0]
                is_required = f'questions[{index}][required]' in form_data

                print(f"\nProcessing question {index}:")
                print(f"  Text: {question_text}")
                print(f"  Type: {question_type}")
                print(f"  Required: {is_required}")

                # Проверяем, есть ли новое изображение
                image_path = None
                if f'questions[{index}][image]' in files:
                    image_file = files[f'questions[{index}][image]'][0]
                    if image_file and image_file.filename:
                        filename = secure_filename(image_file.filename)
                        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        # Сохраняем путь без префикса uploads/
                        image_path = f"questions/{unique_filename}"
                        
                        # Создаем директорию, если она не существует
                        upload_dir = os.path.join('app', 'uploads', 'questions')
                        upload_dir = os.path.join('app', 'uploads', 'questions').replace('\\', '/')
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Сохраняем файл
                        save_path = os.path.join('app', 'uploads', image_path).replace('\\', '/')
                        image_file.save(save_path)
                        print(f"  New image saved: {image_path}")
                else:
                    # Если новое изображение не загружено, используем существующее
                    old_question = old_questions[index] if index < len(old_questions) else None
                    if old_question and old_question.id in existing_images:
                        # Убираем префикс uploads/ из существующего пути, если он есть
                        old_path = existing_images[old_question.id]
                        image_path = old_path[8:] if old_path.startswith('uploads/') else old_path
                        print(f"  Using existing image: {image_path}")

                new_question = question_repository.create_question(
                    survey_id=survey.id,
                    question_text=question_text,
                    question_type=QuestionType(question_type),
                    required=is_required,
                    image_path=image_path
                )
                print(f"  Created new question with ID: {new_question.id}")

                # Обрабатываем ответы
                if question_type in ['single', 'multiple']:
                    answer_key = f'questions[{index}][answers][]'
                    if answer_key in form_data:
                        answers = form_data[answer_key]
                        print(f"  Processing answers for question {index}:")
                        for answer_text in answers:
                            if answer_text.strip():
                                option = question_repository.add_option_to_question(
                                    question_id=new_question.id,
                                    option_text=answer_text
                                )
                                if option:
                                    print(f"    Added answer: {answer_text} (ID: {option.id})")
                                else:
                                    print(f"    Failed to add answer: {answer_text}")

                new_questions.append(new_question)

            print(f"\nCreated {len(new_questions)} new questions")

            db.session.commit()
            print("\nChanges committed to database")
            flash("Опрос обновлен!", "success")
            return redirect(url_for("survey.my_surveys"))

        except Exception as e:
            db.session.rollback()
            print(f"\nError updating survey: {str(e)}")
            flash(f"Произошла ошибка при обновлении опроса: {str(e)}", "danger")
            return redirect(url_for("survey.edit_survey", survey_id=survey_id))

    return render_template("survey/edit.html", survey=survey, questions=survey.questions)
