from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from datetime import datetime, timedelta

from app import db
from models import User, ExpertDetails, QASession, QAQuestion, QAParticipant

expert_bp = Blueprint('expert', __name__, url_prefix='/expert')

@expert_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    """Apply for expert verification."""
    # Check if user already has verification status
    if current_user.verification_status != "unverified":
        if current_user.verification_status == "pending":
            flash('Your verification request is pending review.', 'info')
        elif current_user.verification_status == "verified":
            flash('You are already verified as an expert.', 'info')
        return redirect(url_for('forum.categories'))
    
    if request.method == 'POST':
        profession = request.form.get('profession')
        credentials = request.form.get('credentials')
        bio = request.form.get('bio')
        specialties = request.form.get('specialties')
        verification_documents = request.form.get('verification_documents')
        
        if not profession or not credentials:
            flash('Profession and credentials are required', 'danger')
            return render_template('expert_verification.html')
        
        # Create expert details
        expert_details = ExpertDetails(
            user_id=current_user.id,
            profession=profession,
            credentials=credentials,
            bio=bio,
            specialties=specialties,
            verification_documents=verification_documents
        )
        
        # Update user verification status
        current_user.verification_status = "pending"
        
        db.session.add(expert_details)
        db.session.commit()
        
        flash('Your expert verification request has been submitted. Our team will review it shortly.', 'success')
        return redirect(url_for('forum.categories'))
    
    return render_template('expert_verification.html')

@expert_bp.route('/sessions')
def sessions():
    """Display upcoming Q&A sessions."""
    # Get upcoming and ongoing sessions
    current_time = datetime.utcnow()
    upcoming_sessions = QASession.query.filter(
        QASession.scheduled_time > current_time
    ).order_by(QASession.scheduled_time.asc()).all()
    
    ongoing_sessions = QASession.query.filter(
        QASession.scheduled_time <= current_time,
        QASession.end_time >= current_time,
        QASession.is_active == True
    ).order_by(QASession.scheduled_time.asc()).all()
    
    # Get past sessions (limited to 10)
    past_sessions = QASession.query.filter(
        QASession.end_time < current_time
    ).order_by(QASession.scheduled_time.desc()).limit(10).all()
    
    return render_template('qa_sessions.html', 
                          upcoming_sessions=upcoming_sessions,
                          ongoing_sessions=ongoing_sessions,
                          past_sessions=past_sessions)

@expert_bp.route('/session/<int:session_id>')
def view_session(session_id):
    """View a specific Q&A session."""
    session = QASession.query.get_or_404(session_id)
    current_time = datetime.utcnow()
    
    # Determine session status
    is_upcoming = session.scheduled_time > current_time
    is_ongoing = session.scheduled_time <= current_time and session.end_time >= current_time and session.is_active
    is_past = session.end_time < current_time or session.is_completed
    
    # Get questions for this session
    questions = QAQuestion.query.filter_by(session_id=session_id).order_by(
        QAQuestion.upvotes.desc(), QAQuestion.created_at.asc()).all()
    
    # Check if user is a participant
    is_participant = False
    if current_user.is_authenticated:
        participant = QAParticipant.query.filter_by(session_id=session_id, user_id=current_user.id).first()
        is_participant = participant is not None
    
    return render_template('qa_sessions.html', 
                          session=session,
                          questions=questions,
                          is_upcoming=is_upcoming,
                          is_ongoing=is_ongoing,
                          is_past=is_past,
                          is_participant=is_participant)

@expert_bp.route('/session/<int:session_id>/join', methods=['POST'])
@login_required
def join_session(session_id):
    """Join a Q&A session as a participant."""
    session = QASession.query.get_or_404(session_id)
    current_time = datetime.utcnow()
    
    # Ensure session is upcoming or ongoing
    if session.end_time < current_time or session.is_completed:
        flash('This session has already ended', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Check if user is already a participant
    participant = QAParticipant.query.filter_by(session_id=session_id, user_id=current_user.id).first()
    if participant:
        flash('You are already registered for this session', 'info')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Check if session is full
    current_participants = QAParticipant.query.filter_by(session_id=session_id).count()
    if current_participants >= session.max_participants:
        flash('This session is full', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Add user as participant
    new_participant = QAParticipant(
        session_id=session_id,
        user_id=current_user.id
    )
    
    db.session.add(new_participant)
    db.session.commit()
    
    flash('You have successfully joined the Q&A session!', 'success')
    return redirect(url_for('expert.view_session', session_id=session_id))

@expert_bp.route('/session/<int:session_id>/leave', methods=['POST'])
@login_required
def leave_session(session_id):
    """Leave a Q&A session."""
    session = QASession.query.get_or_404(session_id)
    current_time = datetime.utcnow()
    
    # Ensure session hasn't started yet
    if session.scheduled_time <= current_time and session.is_active:
        flash('Cannot leave an active session', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Find participant record and delete it
    participant = QAParticipant.query.filter_by(session_id=session_id, user_id=current_user.id).first()
    if participant:
        db.session.delete(participant)
        db.session.commit()
        flash('You have left the Q&A session', 'success')
    else:
        flash('You are not registered for this session', 'info')
    
    return redirect(url_for('expert.view_session', session_id=session_id))

@expert_bp.route('/session/<int:session_id>/ask', methods=['POST'])
@login_required
def ask_question(session_id):
    """Ask a question in a Q&A session."""
    session = QASession.query.get_or_404(session_id)
    current_time = datetime.utcnow()
    
    # Ensure session is active
    if not (session.scheduled_time <= current_time and session.end_time >= current_time and session.is_active):
        flash('Questions can only be asked during active sessions', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Ensure user is a participant
    participant = QAParticipant.query.filter_by(session_id=session_id, user_id=current_user.id).first()
    if not participant:
        flash('You must join the session to ask questions', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    question_text = request.form.get('question')
    is_anonymous = 'is_anonymous' in request.form
    
    if not question_text:
        flash('Question cannot be empty', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Create new question
    new_question = QAQuestion(
        session_id=session_id,
        user_id=current_user.id,
        question=question_text,
        is_anonymous=is_anonymous
    )
    
    db.session.add(new_question)
    db.session.commit()
    
    flash('Your question has been submitted!', 'success')
    return redirect(url_for('expert.view_session', session_id=session_id))

@expert_bp.route('/session/<int:session_id>/upvote/<int:question_id>', methods=['POST'])
@login_required
def upvote_question(session_id, question_id):
    """Upvote a question in a Q&A session."""
    session = QASession.query.get_or_404(session_id)
    question = QAQuestion.query.get_or_404(question_id)
    
    # Ensure question belongs to session
    if question.session_id != session_id:
        abort(400)
    
    # Ensure user is a participant
    participant = QAParticipant.query.filter_by(session_id=session_id, user_id=current_user.id).first()
    if not participant:
        flash('You must join the session to upvote questions', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    # Increment upvotes (in a real app, you would track which users upvoted)
    question.upvotes += 1
    db.session.commit()
    
    return redirect(url_for('expert.view_session', session_id=session_id))

@expert_bp.route('/create-session', methods=['GET', 'POST'])
@login_required
def create_session():
    """Create a new Q&A session (for experts only)."""
    # Ensure user is a verified expert
    if not current_user.is_expert or current_user.verification_status != "verified":
        flash('Only verified experts can create Q&A sessions', 'danger')
        return redirect(url_for('expert.sessions'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        duration = request.form.get('duration', type=int)
        max_participants = request.form.get('max_participants', type=int, default=30)
        
        if not title or not description or not scheduled_date or not scheduled_time or not duration:
            flash('All fields are required', 'danger')
            return render_template('qa_sessions.html', creating=True)
        
        # Parse date and time
        try:
            scheduled_datetime = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")
            end_datetime = scheduled_datetime + timedelta(minutes=duration)
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return render_template('qa_sessions.html', creating=True)
        
        # Ensure session is in the future
        if scheduled_datetime <= datetime.utcnow():
            flash('Session must be scheduled in the future', 'danger')
            return render_template('qa_sessions.html', creating=True)
        
        # Create new session
        new_session = QASession(
            title=title,
            description=description,
            expert_id=current_user.id,
            scheduled_time=scheduled_datetime,
            end_time=end_datetime,
            max_participants=max_participants
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        flash('Your Q&A session has been created!', 'success')
        return redirect(url_for('expert.sessions'))
    
    return render_template('qa_sessions.html', creating=True)

@expert_bp.route('/session/<int:session_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_session(session_id):
    """Manage a Q&A session (for the expert who created it)."""
    session = QASession.query.get_or_404(session_id)
    
    # Ensure user is the session expert
    if session.expert_id != current_user.id:
        flash('You can only manage your own sessions', 'danger')
        return redirect(url_for('expert.view_session', session_id=session_id))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'start':
            # Start the session
            if session.scheduled_time > datetime.utcnow():
                flash('Sessions can only be started at or after the scheduled time', 'danger')
            else:
                session.is_active = True
                db.session.commit()
                flash('Session has been started!', 'success')
        
        elif action == 'end':
            # End the session
            session.is_active = False
            session.is_completed = True
            db.session.commit()
            flash('Session has been ended', 'success')
        
        elif action == 'answer':
            # Answer a question
            question_id = request.form.get('question_id', type=int)
            answer = request.form.get('answer')
            
            if not question_id or not answer:
                flash('Question ID and answer are required', 'danger')
            else:
                question = QAQuestion.query.get_or_404(question_id)
                if question.session_id != session_id:
                    abort(400)
                
                question.answer = answer
                question.answered_at = datetime.utcnow()
                db.session.commit()
                flash('Question has been answered', 'success')
        
        return redirect(url_for('expert.manage_session', session_id=session_id))
    
    # Get questions for this session
    questions = QAQuestion.query.filter_by(session_id=session_id).order_by(
        QAQuestion.upvotes.desc(), QAQuestion.created_at.asc()).all()
    
    # Get participants
    participants = QAParticipant.query.filter_by(session_id=session_id).all()
    
    return render_template('qa_sessions.html', 
                          session=session,
                          questions=questions,
                          participants=participants,
                          managing=True)
