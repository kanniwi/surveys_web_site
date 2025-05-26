from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from . import models
    
    from app.routes import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)


    from app.routes import main
    app.register_blueprint(main.bp)
    
    from app.routes import question
    app.register_blueprint(question.bp)
    
    from app.routes import survey
    app.register_blueprint(survey.bp)
    
    from app.routes import stats
    app.register_blueprint(stats.bp)

    @app.route('/test')
    def test():
        return "Привет! Приложение работает!"


    app.route('/', endpoint='index')(main.index)
    
    return app

app = create_app()