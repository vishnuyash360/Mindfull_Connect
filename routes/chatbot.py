from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils.chatbot import get_chatbot_response
import logging

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
def index():
    return render_template('chatbot/index.html', title='Support Bot')

@chatbot_bp.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message']
    
    # Log the incoming message
    logging.debug(f"Chatbot received message: {user_message}")
    
    # Get response from the chatbot
    try:
        response = get_chatbot_response(user_message, current_user)
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error generating chatbot response: {str(e)}")
        return jsonify({'error': 'Could not generate a response at this time. Please try again later.'}), 500
