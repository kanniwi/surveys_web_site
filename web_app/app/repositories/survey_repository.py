from app.models import db, Survey, SurveyStatus
from sqlalchemy import func, distinct
from app.models import Question, UserResponse

class SurveyRepository:

    def get_survey_by_id(self, survey_id): 
        return db.session.query(Survey).filter_by(id=survey_id).first()   
    
    def get_surveys_by_user_id(self, user_id):
        return db.session.query(Survey).filter_by(user_id=user_id).all() 

    def get_all_surveys(self):
        return db.session.query(Survey).all()

    def create_survey(self, title, description, user_id, start_date, end_date, status=SurveyStatus.draft): 
        new_survey = Survey(
            title=title,
            description=description,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        db.session.add(new_survey)
        db.session.commit()
        return new_survey

    def update_survey(self, survey_id, **kwargs): 
        survey = self.get_survey_by_id(survey_id)
        allowed_fields = {'title', 'description', 'start_date', 'end_date', 'status'}
        if survey:
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(survey, key, value)
            db.session.commit()

    def delete_survey(self, survey_id):
        survey = self.get_survey_by_id(survey_id)
        if survey:
            db.session.delete(survey)
            db.session.commit()
            
    def get_all_surveys_with_counts(self):
        surveys = self.get_all_surveys()

        survey_ids = [s.id for s in surveys]

        question_counts = dict(
            db.session.query(Question.survey_id, func.count(Question.id))
            .filter(Question.survey_id.in_(survey_ids))
            .group_by(Question.survey_id)
            .all()
        )

        response_counts = dict(
            db.session.query(UserResponse.survey_id, func.count(distinct(UserResponse.user_id)))
            .filter(UserResponse.survey_id.in_(survey_ids))
            .group_by(UserResponse.survey_id)
            .all()
        )

        result = []
        for survey in surveys:
            result.append({
                'survey': survey,
                'question_count': question_counts.get(survey.id, 0),
                'response_count': response_counts.get(survey.id, 0)
            })

        return result