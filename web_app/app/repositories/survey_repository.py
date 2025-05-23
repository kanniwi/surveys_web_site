from app.models import db, Survey, SurveyStatus, Question, UserResponse
from sqlalchemy import func, distinct
from collections import Counter

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


    def get_survey_with_stats(self, survey_id):
        survey = Survey.query \
            .options(
                db.joinedload(Survey.questions)
                    .joinedload(Question.options),
                db.joinedload(Survey.questions)
                    .joinedload(Question.user_responses)
                    .joinedload(UserResponse.user)
            ) \
            .filter(Survey.id == survey_id) \
            .first()


        if not survey:
            return None

        vote_counts = (
            db.session.query(
                UserResponse.option_id,
                func.count(UserResponse.id)
            )
            .filter(UserResponse.option_id.isnot(None))
            .group_by(UserResponse.option_id)
            .all()
        )
        vote_count_dict = {option_id: count for option_id, count in vote_counts}

        for question in survey.questions:
            if question.question_type.value == 'text':
                texts = [resp.text_answer for resp in question.user_responses if resp.text_answer]
                counter = Counter(texts)
                question.text_stats = [{"text": text, "count": count} for text, count in counter.items()]
            else:
                for option in question.options:
                    option.vote_count = vote_count_dict.get(option.id, 0)


            gender_counts = {
                'male': {},
                'female': {},
                'not_s': {},
                'other': {}            
            }

            if question.question_type.value != 'text':
                for option in question.options:
                    male_count = sum(1 for resp in question.user_responses
                                    if resp.option_id == option.id and resp.user and resp.user.gender == 'male')
                    female_count = sum(1 for resp in question.user_responses
                                    if resp.option_id == option.id and resp.user and resp.user.gender == 'female')
                    not_selected_count = sum(1 for resp in question.user_responses
                                    if resp.option_id == option.id and resp.user and resp.user.gender == 'not_s')
                    other_count = sum(1 for resp in question.user_responses
                                    if resp.option_id == option.id and resp.user and resp.user.gender == 'other')
                    gender_counts['male'][option.option_text] = male_count
                    gender_counts['female'][option.option_text] = female_count
                    gender_counts['not_s'][option.option_text] = not_selected_count
                    gender_counts['other'][option.option_text] = other_count
                    
                    
            # else:
            #     pass

            question.gender_counts = gender_counts

        return survey
