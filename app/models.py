from app import db
from datetime import datetime, timezone

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.String, primary_key=True)
    text = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    sentiment = db.Column(db.String, nullable=False)
    
    def __init__(self, id, text, sentiment):
        self.id = id
        self.text = text
        self.sentiment = sentiment

class Feature(db.Model):
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'), nullable=False)
    code = db.Column(db.String, nullable=False)
    reason = db.Column(db.String, nullable=False)
    
    post = db.relationship('Post', backref=db.backref('features', lazy=True))
    
    def __init__(self, code, reason, post=None):
        self.code = code
        self.reason = reason
        if post:
            self.post = post