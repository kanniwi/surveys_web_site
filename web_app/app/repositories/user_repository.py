from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db, User

class UserRepository:
    def get_user_by_id(self, user_id):
        return db.session.query(User).filter_by(id=user_id).first()
    
    def get_user_by_username(self, username):
        return db.session.query(User).filter_by(username=username).first()
    
    def get_user_by_username_and_password(self, username, password):
        user = db.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
    
    def all(self):
        return db.session.query(User).all()
    
    def create(self, username, email, password, role):
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
        
    def update(self, user_id, username=None, name=None, surname=None, birth_date=None, email=None, password=None, gender=None, role=None):
        user = self.get_user_by_id(user_id)
        print(birth_date)
        if user:
            if username:
                user.username = username
            if email:
                user.email = email
            if name:
                user.name = name
            if surname:
                user.surname = surname
            if birth_date:
                user.birth_date = birth_date
            if password:
                user.password_hash = generate_password_hash(password)
            if gender:
                user.gender=gender
            if role:
                user.role = role
            db.session.commit()
            
    def delete(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            
    def update_password(self, user_id, new_password):
        user = self.get_user_by_id(user_id)
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
    def exists_by_username(self, username):
        return db.session.query(User.id).filter_by(username=username).first() is not None

            
    
    
    
    
    