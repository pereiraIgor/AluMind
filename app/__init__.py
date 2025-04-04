from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from .scheduler import init_scheduler
import os

db = SQLAlchemy()
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY')
    
    init_scheduler(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app