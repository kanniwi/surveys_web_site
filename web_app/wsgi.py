from app import create_app
from flask import render_template

application = create_app()

if __name__ == '__main__':
    application.run(debug=True)