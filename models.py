from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from demo import db
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'
        self.is_expert = False
    
    def get_id(self):
        return None

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    display_name = db.Column(db.String(64), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    forum_topics = db.relationship('ForumTopic', backref='author', lazy='dynamic')
    forum_posts = db.relationship('ForumPost', backref='author', lazy='dynamic')
    mood_entries = db.relationship('MoodEntry', backref='user', lazy='dynamic')
    journals = db.relationship('Journal', backref='user', lazy='dynamic')
    expert_profile = db.relationship('Expert', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_expert(self):
        return self.expert_profile is not None and self.expert_profile.is_verified
    
    def __repr__(self):
        return f'<User {self.username}>'

class ForumTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(50), nullable=False)
    views = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    sentiment_score = db.Column(db.Float, nullable=True)
    
    # Relationships
    posts = db.relationship('ForumPost', backref='topic', lazy='dynamic')
    
    def __repr__(self):
        return f'<ForumTopic {self.title}>'

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topic.id'))
    is_solution = db.Column(db.Boolean, default=False)
    sentiment_score = db.Column(db.Float, nullable=True)
    
    # Relationships
    reports = db.relationship('Report', backref='post', lazy='dynamic')
    
    def __repr__(self):
        return f'<ForumPost {self.id}>'

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mood_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    
    def __repr__(self):
        return f'<MoodEntry {self.mood_level}>'

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<Journal {self.title}>'

class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    credentials = db.Column(db.Text, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    qa_sessions = db.relationship('QASession', backref='expert', lazy='dynamic')
    
    def __repr__(self):
        return f'<Expert {self.id}>'

class QASession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    max_participants = db.Column(db.Integer, default=20)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QASession {self.title}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, resolved, dismissed
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f'<Report {self.id}>'
