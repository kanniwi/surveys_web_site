from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('main/index.html')

# @bp.route('/catalog')
# def catalog():
#     return render_template('main/catalog.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')



