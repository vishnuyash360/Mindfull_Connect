from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from models import User, MoodEntry, Journal
from utils.sentiment import analyze_sentiment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import datetime, timedelta
from demo import db

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

class JournalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=255)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    is_private = BooleanField('Keep Private', default=True)
    submit = SubmitField('Save Journal Entry')

class MoodForm(FlaskForm):
    mood_level = IntegerField('Mood (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Mood')

class ProfileForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=64)])
    submit = SubmitField('Update Profile')

@profile_bp.route('/dashboard')
@login_required
def dashboard():
    # Get recent mood entries in chronological order for the chart
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.created_at).limit(7).all()
    
    # Get recent journal entries
    journal_entries = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.created_at.desc()).limit(5).all()
    
    # Calculate average mood for past week
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_moods = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= week_ago
    ).all()
    
    avg_mood = sum([mood.mood_level for mood in week_moods]) / len(week_moods) if week_moods else 0
    
    # Prepare mood data for the chart
    mood_data = {
        'labels': [entry.created_at.strftime('%m/%d') for entry in mood_entries],
        'values': [entry.mood_level for entry in mood_entries],
        'notes': [entry.notes or '' for entry in mood_entries],
        'tags': [entry.tags or '' for entry in mood_entries]
    }

    return render_template('profile/dashboard.html',
                          title='Dashboard',
                          mood_entries=mood_entries,
                          journal_entries=journal_entries,
                          avg_mood=avg_mood,
                          mood_data=mood_data)

@profile_bp.route('/mood-tracker', methods=['GET', 'POST'])
@login_required
def mood_tracker():
    form = MoodForm()
    if form.validate_on_submit():
        mood_entry = MoodEntry(
            user_id=current_user.id,
            mood_level=form.mood_level.data,
            notes=form.notes.data,
            tags=form.tags.data
        )
        
        db.session.add(mood_entry)
        db.session.commit()
        
        flash('Your mood has been recorded!', 'success')
        return redirect(url_for('profile.mood_tracker'))
    
    # Get mood entries for the past 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= thirty_days_ago
    ).order_by(MoodEntry.created_at).all()
    
    # Format data for chart.js
    mood_data = {
        'labels': [entry.created_at.strftime('%Y-%m-%d') for entry in mood_entries],
        'values': [entry.mood_level for entry in mood_entries]
    }
    
    return render_template('profile/mood-tracker.html',
                          title='Mood Tracker',
                          form=form,
                          mood_entries=mood_entries,
                          mood_data=mood_data)

@profile_bp.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    form = JournalForm()
    if form.validate_on_submit():
        journal_entry = Journal(
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            is_private=form.is_private.data
        )
        
        # Analyze sentiment
        sentiment_score = analyze_sentiment(form.content.data)
        journal_entry.sentiment_score = sentiment_score
        
        db.session.add(journal_entry)
        db.session.commit()
        
        flash('Your journal entry has been saved!', 'success')
        return redirect(url_for('profile.journal'))
    
    # Get all journal entries
    journal_entries = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.created_at.desc()).all()
    
    return render_template('profile/journal.html',
                          title='Journal',
                          form=form,
                          journal_entries=journal_entries)

@profile_bp.route('/journal/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def view_journal(entry_id):
    entry = Journal.query.get_or_404(entry_id)
    
    # Ensure the user owns this journal entry
    if entry.user_id != current_user.id:
        abort(403)
    
    form = JournalForm()
    
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        entry.is_private = form.is_private.data
        
        # Re-analyze sentiment
        sentiment_score = analyze_sentiment(form.content.data)
        entry.sentiment_score = sentiment_score
        
        db.session.commit()
        
        flash('Your journal entry has been updated!', 'success')
        return redirect(url_for('profile.journal'))
    
    elif request.method == 'GET':
        form.title.data = entry.title
        form.content.data = entry.content
        form.is_private.data = entry.is_private
    
    return render_template('profile/journal.html',
                          title='Edit Journal Entry',
                          form=form,
                          journal_entries=None,
                          edit_mode=True,
                          entry=entry)

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.settings'))
    
    elif request.method == 'GET':
        form.display_name.data = current_user.display_name
    
    return render_template('profile/settings.html', title='Profile Settings', form=form)

@profile_bp.route('/api/mood-data')
@login_required
def mood_data():
    days = request.args.get('days', 30, type=int)
    
    period_start = datetime.utcnow() - timedelta(days=days)
    
    # Get mood entries for the specified period
    mood_entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= period_start
    ).order_by(MoodEntry.created_at).all()
    
    # Format data for chart.js
    data = {
        'labels': [entry.created_at.strftime('%Y-%m-%d') for entry in mood_entries],
        'values': [entry.mood_level for entry in mood_entries],
        'notes': [entry.notes for entry in mood_entries],
        'tags': [entry.tags for entry in mood_entries]
    }
    
    return jsonify(data)
