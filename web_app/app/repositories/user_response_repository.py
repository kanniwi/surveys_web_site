from app.models import db, UserResponse

class UserResponseRepository:
    def save_response(self, user_id, survey_id, question_id, option_id=None, text_answer=None):
        response = UserResponse(
            user_id=user_id,
            survey_id=survey_id,
            question_id=question_id,
            option_id=option_id,
            text_answer=text_answer
        )
        db.session.add(response)
        db.session.commit()

    def get_responses_by_user(self, user_id):
        return db.session.query(UserResponse).filter_by(user_id=user_id).all()

    def get_responses_by_survey(self, survey_id):
        return db.session.query(UserResponse).filter_by(survey_id=survey_id).all()

    def get_responses_by_question(self, question_id):
        return db.session.query(UserResponse).filter_by(question_id=question_id).all()

    def get_response(self, user_id, question_id):
        return db.session.query(UserResponse).filter_by(user_id=user_id, question_id=question_id).first()

    def delete_response(self, response_id):
        response = db.session.query(UserResponse).filter_by(id=response_id).first()
        if response:
            db.session.delete(response)
            db.session.commit()

    def update_text_answer(self, response_id, new_text):
        response = db.session.query(UserResponse).filter_by(id=response_id).first()
        if response:
            response.text_answer = new_text
            db.session.commit()

    def get_user_responses_for_survey(self, user_id, survey_id):
        return db.session.query(UserResponse).filter_by(
            user_id=user_id,
            survey_id=survey_id
        ).first()
