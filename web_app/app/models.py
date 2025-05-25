from app import db
import enum
from flask_login import UserMixin
from datetime import datetime, timezone

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    gender = db.Column(db.String(10), default='not_s', nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)     
    role = db.Column(db.Enum(UserRole), default=UserRole.guest, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_blocked = db.Column(db.Boolean, default=False)

    
    surveys = db.relationship('Survey', back_populates='author', lazy=True)
    user_responses = db.relationship('UserResponse', back_populates='user', lazy=True, cascade='all, delete-orphan')
    
    
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
    start_date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    end_date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime(2999, 12, 31, tzinfo=timezone.utc),
        nullable=True
    )
    status = db.Column(db.Enum(SurveyStatus), default=SurveyStatus.draft, nullable=False)

    author = db.relationship('User', back_populates='surveys', lazy=True)
    questions = db.relationship('Question', back_populates='survey', lazy='joined', cascade='all, delete-orphan')
    user_responses = db.relationship('UserResponse', back_populates='survey', lazy=True, cascade='all, delete-orphan')

    def is_active(self):
        now = datetime.now(timezone.utc)
        def make_aware(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        start = make_aware(self.start_date)
        end = make_aware(self.end_date)

        return start <= now <= end

    
    
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
    image_path = db.Column(db.String(255), nullable=True)
    required = db.Column(db.Boolean, default=False, nullable=False)

    survey = db.relationship('Survey', back_populates='questions', lazy='joined')
    options = db.relationship('Option', back_populates='question', lazy='joined', cascade='all, delete-orphan')
    user_responses = db.relationship('UserResponse', back_populates='question', lazy=True, cascade='all, delete-orphan')
    
    
class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    
    question = db.relationship('Question', back_populates='options', lazy=True)
    user_responses = db.relationship('UserResponse', back_populates='option', lazy=True, cascade='all, delete-orphan')
    

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
    
    
    



