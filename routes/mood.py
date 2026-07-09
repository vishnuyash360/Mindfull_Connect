from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
import json

from app import db
from models import MoodEntry, Journal
from utils.sentiment_analysis import analyze_sentiment

mood_bp = Blueprint('mood', __name__, url_prefix='/mood')
from flask import jsonify

@mood_bp.route("/api/mood-data")
@login_required
def mood_data():

    entries = MoodEntry.query.filter_by(
        user_id=current_user.id
    ).order_by(MoodEntry.created_at.asc()).all()

    return jsonify({
        "labels":[
            e.created_at.strftime("%d %b")
            for e in entries
        ],
        "values":[
            e.mood_level
            for e in entries
        ],
        "notes":[
            e.notes or ""
            for e in entries
        ],
        "tags":[
            e.tags or ""
            for e in entries
        ]
    })
@mood_bp.route('/tracker')
@login_required
def tracker():
    """Display the mood tracker page."""
    # Get last 30 days of mood entries
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).filter(
        MoodEntry.created_at >= thirty_days_ago).order_by(MoodEntry.created_at.desc()).all()
    
    # Format data for Chart.js
    dates = [entry.created_at.strftime('%Y-%m-%d') for entry in mood_entries]
    mood_levels = [entry.mood_level for entry in mood_entries]
    
    return render_template('mood_tracker.html', 
                          mood_entries=mood_entries, 
                          mood_data=json.dumps({'dates': dates, 'mood_levels': mood_levels}))

@mood_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_mood():
    """Add a new mood entry."""
    if request.method == 'POST':
        mood_level = request.form.get('mood_level', type=int)
        mood_description = request.form.get('mood_description')
        notes = request.form.get('notes')
        sleep_hours = request.form.get('sleep_hours', type=float)
        exercise_minutes = request.form.get('exercise_minutes', type=int)
        social_interaction = request.form.get('social_interaction', type=int)
        
        if not mood_level or mood_level < 1 or mood_level > 10:
            flash('Please provide a valid mood level (1-10)', 'danger')
            return redirect(url_for('mood.tracker'))
        
        # Create new mood entry
        new_entry = MoodEntry(
            user_id=current_user.id,
            mood_level=mood_level,
            mood_description=mood_description,
            notes=notes,
            sleep_hours=sleep_hours,
            exercise_minutes=exercise_minutes,
            social_interaction_level=social_interaction
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        flash('Your mood has been recorded!', 'success')
        return redirect(url_for('mood.tracker'))
    
    return render_template('mood_tracker.html', adding=True)

@mood_bp.route('/journal')
@login_required
def journal():
    """Display the journal entries."""
    entries = Journal.query.filter_by(user_id=current_user.id).order_by(
        Journal.created_at.desc()).all()
    
    return render_template('journal.html', entries=entries)

@mood_bp.route('/journal/add', methods=['GET', 'POST'])
@login_required
def add_journal():
    """Add a new journal entry."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        mood_tags = request.form.get('mood_tags')
        
        if not content:
            flash('Journal content is required', 'danger')
            return render_template('journal.html', adding=True)
        
        # Perform sentiment analysis
        sentiment_score = analyze_sentiment(content)
        
        # Create new journal entry
        new_entry = Journal(
            user_id=current_user.id,
            title=title,
            content=content,
            mood_tags=mood_tags,
            sentiment_score=sentiment_score
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        flash('Your journal entry has been saved!', 'success')
        return redirect(url_for('mood.journal'))
    
    return render_template('journal.html', adding=True)

@mood_bp.route('/journal/<int:entry_id>')
@login_required
def view_journal(entry_id):
    """View a specific journal entry."""
    entry = Journal.query.get_or_404(entry_id)
    
    # Ensure user owns the journal entry
    if entry.user_id != current_user.id:
        flash('You do not have permission to view this entry', 'danger')
        return redirect(url_for('mood.journal'))
    
    return render_template('journal.html', entry=entry, viewing=True)

@mood_bp.route('/journal/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal(entry_id):
    """Edit a journal entry."""
    entry = Journal.query.get_or_404(entry_id)
    
    # Ensure user owns the journal entry
    if entry.user_id != current_user.id:
        flash('You do not have permission to edit this entry', 'danger')
        return redirect(url_for('mood.journal'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        mood_tags = request.form.get('mood_tags')
        
        if not content:
            flash('Journal content is required', 'danger')
            return render_template('journal.html', entry=entry, editing=True)
        
        # Update sentiment score
        sentiment_score = analyze_sentiment(content)
        
        # Update journal entry
        entry.title = title
        entry.content = content
        entry.mood_tags = mood_tags
        entry.sentiment_score = sentiment_score
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Your journal entry has been updated!', 'success')
        return redirect(url_for('mood.view_journal', entry_id=entry.id))
    
    return render_template('journal.html', entry=entry, editing=True)

@mood_bp.route('/journal/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_journal(entry_id):
    """Delete a journal entry."""
    entry = Journal.query.get_or_404(entry_id)
    
    # Ensure user owns the journal entry
    if entry.user_id != current_user.id:
        flash('You do not have permission to delete this entry', 'danger')
        return redirect(url_for('mood.journal'))
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Your journal entry has been deleted!', 'success')
    return redirect(url_for('mood.journal'))

@mood_bp.route('/insights')
@login_required
def insights():
    """Display mood insights and patterns."""
    # Get all mood entries for the user
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(
        MoodEntry.created_at.asc()).all()
    
    # No insights if not enough data
    if len(mood_entries) < 5:
        flash('Record at least 5 mood entries to see insights', 'info')
        return redirect(url_for('mood.tracker'))
    
    # Calculate average mood
    avg_mood = sum(entry.mood_level for entry in mood_entries) / len(mood_entries)
    
    # Find mood trends (last 7 days vs previous 7 days)
    last_week = datetime.utcnow() - timedelta(days=7)
    previous_week = last_week - timedelta(days=7)
    
    last_week_entries = [
        entry for entry in mood_entries 
        if entry.created_at >= last_week
    ]
    
    previous_week_entries = [
        entry for entry in mood_entries 
        if previous_week <= entry.created_at < last_week
    ]
    
    last_week_avg = sum(entry.mood_level for entry in last_week_entries) / len(last_week_entries) if last_week_entries else 0
    previous_week_avg = sum(entry.mood_level for entry in previous_week_entries) / len(previous_week_entries) if previous_week_entries else 0
    
    # Analyze sleep correlation if data available
    sleep_data = [(entry.sleep_hours, entry.mood_level) for entry in mood_entries if entry.sleep_hours]
    
    # Analyze exercise correlation if data available
    exercise_data = [(entry.exercise_minutes, entry.mood_level) for entry in mood_entries if entry.exercise_minutes]
    
    # Analyze social interaction correlation if data available
    social_data = [(entry.social_interaction_level, entry.mood_level) for entry in mood_entries if entry.social_interaction_level]
    
    return render_template('mood_tracker.html', 
                          insights=True,
                          avg_mood=avg_mood,
                          last_week_avg=last_week_avg,
                          previous_week_avg=previous_week_avg,
                          sleep_data=json.dumps(sleep_data) if sleep_data else None,
                          exercise_data=json.dumps(exercise_data) if exercise_data else None,
                          social_data=json.dumps(social_data) if social_data else None)
