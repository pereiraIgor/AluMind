from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY')
    
    from .scheduler import init_scheduler
    init_scheduler(app)

    db.init_app(app)
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app