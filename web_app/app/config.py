import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False