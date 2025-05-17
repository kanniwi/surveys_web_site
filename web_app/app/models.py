from app import db
import enum
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)     
    role = db.Column(db.Enum(UserRole), default=UserRole.guest, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    surveys = db.relationship('Survey', back_populates='author', lazy=True)
    user_responses = db.relationship('UserResponse', back_populates='user', lazy=True)
    
    
class SurveyStatus(enum.Enum):
    active = "active"
    draft = "draft"
    closed = "closed"
    
class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(SurveyStatus), default=SurveyStatus.draft, nullable=False)
    
    author = db.relationship('User', back_populates='surveys', lazy=True)
    questions = db.relationship('Question', back_populates='survey', lazy='joined')
    user_responses = db.relationship('UserResponse', back_populates='survey', lazy=True)
    
    
class QuestionType(enum.Enum):
    single = "single"
    multiple = "multiple"
    text = "text"

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    
    survey = db.relationship('Survey', back_populates='questions', lazy='joined')
    options = db.relationship('Option', back_populates='question', lazy='joined')
    user_responses = db.relationship('UserResponse', back_populates='question', lazy=True)
    
    
class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    
    question = db.relationship('Question', back_populates='options', lazy=True)
    user_responses = db.relationship('UserResponse', back_populates='option', lazy=True)
    

class UserResponse(db.Model):
    __tablename__ = 'user_responses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)
    answered_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user = db.relationship('User', back_populates='user_responses', lazy=True)
    survey = db.relationship('Survey', back_populates='user_responses', lazy=True)
    question = db.relationship('Question', back_populates='user_responses', lazy=True)
    option = db.relationship('Option', back_populates='user_responses', lazy=True)
    
    
    



