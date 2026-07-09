from flask import Blueprint, render_template
from flask_login import current_user

mindfulness_bp = Blueprint('mindfulness', __name__, url_prefix='/mindfulness')

@mindfulness_bp.route('/')
def index():
    return render_template('mindfulness/index.html', title='Mindfulness Resources')

@mindfulness_bp.route('/meditation')
def meditation():
    return render_template('mindfulness/meditation.html', title='Meditation Timer')

@mindfulness_bp.route('/exercises')
def exercises():
    return render_template('mindfulness/exercises.html', title='Mindfulness Exercises')

@mindfulness_bp.route('/breathing')
def breathing():
    return render_template('mindfulness/breathing.html', title='Breathing Exercises')

@mindfulness_bp.route('/gratitude')
def gratitude():
    return render_template('mindfulness/gratitude.html', title='Gratitude Practice')
