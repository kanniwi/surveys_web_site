from flask import Blueprint

bp = Blueprint('question', __name__, url_prefix='/questions')


@bp.route('/create', methods=['POST'])
def create_question():
    pass

# Редактирование вопроса
@bp.route('/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    pass

# Удаление вопроса
@bp.route('/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    pass

# Добавление варианта ответа к вопросу
@bp.route('/<int:question_id>/options/add', methods=['POST'])
def add_option(question_id):
    pass

# Удаление варианта
@bp.route('/options/<int:option_id>/delete', methods=['POST'])
def delete_option(option_id):
    pass

# Редактирование варианта ответа
@bp.route('/options/<int:option_id>/edit', methods=['POST'])
def edit_option(option_id):
    pass
