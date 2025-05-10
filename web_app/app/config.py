
# MYSQL_USER = 'kanniwi'
# MYSQL_PASSWORD = 'Mospolytech2025!'
# MYSQL_HOST = 'kanniwi.mysql.pythonanywhere-services.com'
# MYSQL_DATABASE = 'kanniwi$default'

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'survey_db'

SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
f"@{MYSQL_HOST}/{MYSQL_DATABASE}"

SQLALCHEMY_TRACK_MODIFICATIONS = False