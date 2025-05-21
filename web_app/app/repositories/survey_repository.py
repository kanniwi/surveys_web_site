from app.models import db, Survey, SurveyStatus

class SurveyRepository:

    def get_survey_by_id(self, survey_id): 
        return db.session.query(Survey).filter_by(id=survey_id).first()   
    
    def get_surveys_by_user_id(self, user_id):
        return db.session.query(Survey).filter_by(user_id=user_id).all() 

    def get_all_surveys(self):
        return db.session.query(Survey).all()

    def create_survey(self, title, description, user_id, start_date, end_date=None, status=SurveyStatus.draft): 
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
