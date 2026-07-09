from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import Expert, QASession, User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import datetime

experts_bp = Blueprint('experts', __name__, url_prefix='/experts')

class ExpertVerificationForm(FlaskForm):
    credentials = TextAreaField('Professional Credentials', validators=[DataRequired(), Length(min=50, max=2000)])
    specialization = StringField('Area of Specialization', validators=[DataRequired(), Length(min=3, max=100)])
    bio = TextAreaField('Professional Bio', validators=[DataRequired(), Length(min=100, max=5000)])
    submit = SubmitField('Submit Application')

class QASessionForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(min=5, max=255)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20, max=2000)])
    scheduled_at = DateTimeField('Scheduled Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=15, max=180)])
    max_participants = IntegerField('Maximum Participants', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Schedule Session')

@experts_bp.route('/')
def index():
    # Get verified experts
    experts = Expert.query.filter_by(is_verified=True).all()
    
    # Get upcoming Q&A sessions
    now = datetime.utcnow()
    upcoming_sessions = QASession.query.filter(
        QASession.scheduled_at > now,
        QASession.is_active == True
    ).order_by(QASession.scheduled_at).all()
    
    return render_template('experts/index.html',
                          title='Mental Health Experts',
                          experts=experts,
                          upcoming_sessions=upcoming_sessions)

@experts_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    # Check if the user already has an expert profile
    existing_profile = Expert.query.filter_by(user_id=current_user.id).first()
    
    if existing_profile:
        if existing_profile.is_verified:
            flash('You are already verified as an expert.', 'info')
            return redirect(url_for('experts.dashboard'))
        else:
            flash('Your verification application is pending review.', 'info')
            return redirect(url_for('index'))
    
    form = ExpertVerificationForm()
    
    if form.validate_on_submit():
        expert = Expert(
            user_id=current_user.id,
            credentials=form.credentials.data,
            specialization=form.specialization.data,
            bio=form.bio.data,
            is_verified=False  # Will be verified by admin
        )
        
        db.session.add(expert)
        db.session.commit()
        
        flash('Your expert verification application has been submitted and is pending review.', 'success')
        return redirect(url_for('index'))
    
    return render_template('experts/verify.html',
                          title='Expert Verification',
                          form=form)

@experts_bp.route('/dashboard')
@login_required
def dashboard():
    # Ensure the user is a verified expert
    if not current_user.is_expert:
        flash('You must be a verified expert to access this page.', 'warning')
        return redirect(url_for('experts.verify'))
    
    # Get expert profile
    expert = Expert.query.filter_by(user_id=current_user.id).first()
    
    # Get upcoming sessions for this expert
    now = datetime.utcnow()
    upcoming_sessions = QASession.query.filter(
        QASession.expert_id == expert.id,
        QASession.scheduled_at > now
    ).order_by(QASession.scheduled_at).all()
    
    # Get past sessions
    past_sessions = QASession.query.filter(
        QASession.expert_id == expert.id,
        QASession.scheduled_at <= now
    ).order_by(QASession.scheduled_at.desc()).all()
    
    return render_template('experts/dashboard.html',
                          title='Expert Dashboard',
                          expert=expert,
                          upcoming_sessions=upcoming_sessions,
                          past_sessions=past_sessions)

@experts_bp.route('/sessions/create', methods=['GET', 'POST'])
@login_required
def create_session():
    # Ensure the user is a verified expert
    if not current_user.is_expert:
        flash('You must be a verified expert to create Q&A sessions.', 'warning')
        return redirect(url_for('experts.verify'))
    
    expert = Expert.query.filter_by(user_id=current_user.id).first()
    
    form = QASessionForm()
    
    if form.validate_on_submit():
        # Ensure the session is scheduled in the future
        if form.scheduled_at.data <= datetime.utcnow():
            flash('Sessions must be scheduled in the future.', 'danger')
            return render_template('experts/sessions.html',
                                  title='Create Q&A Session',
                                  form=form)
        
        session = QASession(
            expert_id=expert.id,
            title=form.title.data,
            description=form.description.data,
            scheduled_at=form.scheduled_at.data,
            duration_minutes=form.duration_minutes.data,
            max_participants=form.max_participants.data,
            is_active=True
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash('Your Q&A session has been scheduled!', 'success')
        return redirect(url_for('experts.dashboard'))
    
    return render_template('experts/sessions.html',
                          title='Create Q&A Session',
                          form=form)

@experts_bp.route('/sessions/<int:session_id>')
def view_session(session_id):
    session = QASession.query.get_or_404(session_id)
    expert = Expert.query.get(session.expert_id)
    
    # Get expert user info
    expert_user = User.query.get(expert.user_id)
    
    return render_template('experts/session.html',
                          title=session.title,
                          session=session,
                          expert=expert,
                          expert_user=expert_user,
                          now=datetime.utcnow() )

@experts_bp.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id):
    session = QASession.query.get_or_404(session_id)
    expert = Expert.query.filter_by(user_id=current_user.id).first()
    
    # Ensure the current user is the expert who created this session
    if not expert or session.expert_id != expert.id:
        abort(403)
    
    session.is_active = False
    db.session.commit()
    
    flash('The Q&A session has been cancelled.', 'success')
    return redirect(url_for('experts.dashboard'))

@experts_bp.route('/expert/<int:expert_id>')
def view_expert(expert_id):
    expert = Expert.query.get_or_404(expert_id)
    
    # Only show verified experts
    if not expert.is_verified:
        abort(404)
    
    expert_user = User.query.get(expert.user_id)
    
    # Get upcoming sessions for this expert
    now = datetime.utcnow()
    upcoming_sessions = QASession.query.filter(
        QASession.expert_id == expert.id,
        QASession.scheduled_at > now,
        QASession.is_active == True
    ).order_by(QASession.scheduled_at).all()
    
    return render_template('experts/view.html',
                          title=f'Expert: {expert_user.display_name}',
                          expert=expert,
                          expert_user=expert_user,
                          upcoming_sessions=upcoming_sessions)
