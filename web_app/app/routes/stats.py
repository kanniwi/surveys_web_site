from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required
from flask import render_template
from app.repositories import SurveyRepository, QuestionRepository, UserResponseRepository

bp = Blueprint('stats', __name__, url_prefix='/stats')

survey_repository = SurveyRepository()


@bp.route('/')
@login_required
def overall_stats():
    pass


@bp.route('/survey/<int:survey_id>')
@login_required
def survey_stats(survey_id):
    survey = survey_repository.get_survey_with_stats(survey_id)

    if not survey:
        flash("Опрос не найден", "danger")
        return redirect(url_for("main.index"))

    return render_template("stats/survey_stats.html", survey=survey)


