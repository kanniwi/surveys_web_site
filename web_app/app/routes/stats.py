from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required
from flask import render_template
from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository
from flask import Response
import csv
from io import StringIO


bp = Blueprint('stats', __name__, url_prefix='/stats')

survey_repository = SurveyRepository()


@bp.route('/survey/<int:survey_id>')
@login_required
def survey_stats(survey_id):
    survey = survey_repository.get_survey_with_stats(survey_id)
    if not survey:
        flash("Опрос не найден", "danger")
        return redirect(url_for('main.index'))

    survey_data = {
        'id': survey.id,
        'title': survey.title,
        'questions': []
    }

    for question in survey.questions:
        question_data = {
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type.value,
            'options': []
        }

        if question.question_type.value == 'text':
            question_data['text_responses'] = question.text_stats
        else:
            for option in question.options:
                option_data = {
                    'id': option.id,
                    'text': option.option_text,
                    'vote_count': option.vote_count,
                    'gender_counts': {
                        'male': question.gender_counts['male'].get(option.option_text, 0),
                        'female': question.gender_counts['female'].get(option.option_text, 0),
                        'not_s': question.gender_counts['not_s'].get(option.option_text, 0)
                    }
                }
                question_data['options'].append(option_data)

        survey_data['questions'].append(question_data)

    return render_template('stats/survey_stats.html', survey=survey, survey_data=survey_data)





@bp.route('/export/<int:survey_id>')
def export_survey_statistics(survey_id):
    survey = survey_repository.get_survey_with_stats(survey_id)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Вопрос №', 'Вопрос', 'Вариант ответа / Ответ', 'Всего', 'Мужчины', 'Женщины', 'Не указано'])

    for idx, question in enumerate(survey.questions, start=1):
        if question.question_type.value == 'text':
            for stat in question.text_stats: 
                writer.writerow([idx, question.question_text, stat['text'], stat['count'], '-', '-', '-'])
        else:
            for option in question.options:
                option_text = option.option_text
                total = option.vote_count or 0
                male = question.gender_counts.get('male', {}).get(option_text, 0)
                female = question.gender_counts.get('female', {}).get(option_text, 0)
                not_s = question.gender_counts.get('not_s', {}).get(option_text, 0)

                writer.writerow([idx, question.question_text, option_text, total, male, female, not_s])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename=survey_{survey_id}_statistics.csv"}
    )



