from app.models import db, Question, Option

class QuestionRepository:
    def get_question_by_id(self, question_id):
        return db.session.query(Question).filter_by(id=question_id).first()
    
    def get_questions_by_survey_id(self, survey_id):
        return db.session.query(Question).filter_by(survey_id=survey_id).all()
    
    def create_question(self, survey_id, question_text, question_type):
        new_question = Question(
            survey_id=survey_id,
            question_text=question_text,
            question_type=question_type
        )
        db.session.add(new_question)
        db.session.commit()
        return new_question
    
    def update_question(self, question_id, **kwargs):
        question = self.get_question_by_id(question_id)
        allowed_fields = {'question_text', 'question_type'}
        if question:
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(question, key, value)
            db.session.commit()
            
    def delete_question(self, question_id):
        question = db.session.query(Question).filter_by(id=question_id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
            
    def add_option_to_question(self, question_id, option_text):
        question = self.get_question_by_id(question_id)
        if question:
            new_option = Option(
                question_id=question.id,
                option_text=option_text
            )
            db.session.add(new_option)
            db.session.commit()
            
    def update_option(self, option_id, **kwargs):
        option = db.session.query(Option).filter_by(id=option_id).first()
        allowed_fields = {'option_text'}
        if option:
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(option, key, value)
            db.session.commit()
    
    def delete_option(self, option_id):
        option = db.session.query(Option).filter_by(id=option_id).first()
        if option:
            db.session.delete(option)
            db.session.commit()
            
    def delete_all_options_for_question(self, question_id):
        options = db.session.query(Option).filter_by(question_id=question_id).all()
        for option in options:
            db.session.delete(option)
        db.session.commit()
    
    def get_options_for_question(self, question_id):
        return db.session.query(Option).filter_by(question_id=question_id).all()

