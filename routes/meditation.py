from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

meditation_bp = Blueprint('meditation', __name__, url_prefix='/meditation')

@meditation_bp.route('/')
def index():
    """Display the meditation page with timer."""
    return render_template('meditation.html')

@meditation_bp.route('/mindfulness')
def mindfulness():
    """Display mindfulness exercises and guides."""
    return render_template('mindfulness.html')

@meditation_bp.route('/timer/<int:minutes>')
def timer(minutes):
    """Start a meditation timer for specified minutes."""
    # Validate minutes (between 1 and 60)
    if minutes < 1 or minutes > 60:
        flash('Please select a valid meditation duration (1-60 minutes)', 'danger')
        return redirect(url_for('meditation.index'))
    
    return render_template('meditation.html', timer_minutes=minutes)

@meditation_bp.route('/breathing')
def breathing_exercises():
    """Display breathing exercises."""
    return render_template('mindfulness.html', breathing=True)

@meditation_bp.route('/body-scan')
def body_scan():
    """Display body scan meditation guidance."""
    return render_template('mindfulness.html', body_scan=True)

@meditation_bp.route('/gratitude')
def gratitude_practice():
    """Display gratitude practice guidance."""
    return render_template('mindfulness.html', gratitude=True)

@meditation_bp.route('/stress-relief')
def stress_relief():
    """Display stress relief techniques."""
    return render_template('mindfulness.html', stress_relief=True)
