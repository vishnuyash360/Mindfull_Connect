from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime
import uuid

from app import db
from models import ChatbotConversation, ChatbotMessage
from utils.chatbot_rules import get_chatbot_response
from utils.sentiment_analysis import analyze_sentiment

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
def index():
    """Display the chatbot interface."""
    # Create a new conversation ID if user isn't authenticated
    conversation_id = str(uuid.uuid4())
    
    # For authenticated users, load or create a conversation
    if current_user.is_authenticated:
        # Get the most recent conversation or create a new one
        conversation = ChatbotConversation.query.filter_by(user_id=current_user.id).order_by(
            ChatbotConversation.last_message_at.desc()).first()
        
        if conversation:
            conversation_id = conversation.conversation_id
        else:
            # Create a new conversation for the user
            new_conversation = ChatbotConversation(
                user_id=current_user.id,
                conversation_id=conversation_id
            )
            db.session.add(new_conversation)
            db.session.commit()
    
    return render_template('chat.html', conversation_id=conversation_id)

@chat_bp.route('/new')
@login_required
def new_conversation():
    """Start a new conversation with the chatbot."""
    # Create a new conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Create a new conversation for the user
    new_conversation = ChatbotConversation(
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    db.session.add(new_conversation)
    db.session.commit()
    
    return redirect(url_for('chat.index'))

@chat_bp.route('/history')
@login_required
def history():
    """View chat history."""
    conversations = ChatbotConversation.query.filter_by(user_id=current_user.id).order_by(
        ChatbotConversation.last_message_at.desc()).all()
    
    return render_template('chat.html', conversations=conversations, viewing_history=True)

@chat_bp.route('/view/<string:conversation_id>')
@login_required
def view_conversation(conversation_id):
    """View a specific conversation."""
    # Get the conversation
    conversation = ChatbotConversation.query.filter_by(
        user_id=current_user.id, conversation_id=conversation_id).first_or_404()
    
    # Get messages
    messages = ChatbotMessage.query.filter_by(conversation_id=conversation.id).order_by(
        ChatbotMessage.created_at.asc()).all()
    
    return render_template('chat.html', conversation=conversation, messages=messages)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Send a message to the chatbot and get a response."""
    message = request.form.get('message')
    conversation_id = request.form.get('conversation_id')
    
    if not message or not conversation_id:
        return jsonify({'error': 'Message and conversation ID are required'}), 400
    
    # Get or create conversation in database
    conversation = None
    
    if current_user.is_authenticated:
        conversation = ChatbotConversation.query.filter_by(
            user_id=current_user.id, conversation_id=conversation_id).first()
        
        if not conversation:
            conversation = ChatbotConversation(
                user_id=current_user.id,
                conversation_id=conversation_id
            )
            db.session.add(conversation)
            db.session.commit()
    
    # Analyze sentiment of user message
    sentiment_score = analyze_sentiment(message)
    
    # Save user message if authenticated
    if current_user.is_authenticated and conversation:
        user_message = ChatbotMessage(
            conversation_id=conversation.id,
            is_user_message=True,
            content=message,
            sentiment_score=sentiment_score
        )
        db.session.add(user_message)
        
        # Update conversation last message time
        conversation.last_message_at = datetime.utcnow()
        db.session.commit()
    
    # Generate chatbot response
    response = get_chatbot_response(message, sentiment_score)
    
    # Save chatbot response if authenticated
    if current_user.is_authenticated and conversation:
        bot_message = ChatbotMessage(
            conversation_id=conversation.id,
            is_user_message=False,
            content=response
        )
        db.session.add(bot_message)
        db.session.commit()
    
    return jsonify({
        'response': response,
        'sentiment': sentiment_score
    })

@chat_bp.route('/delete/<string:conversation_id>', methods=['POST'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation."""
    conversation = ChatbotConversation.query.filter_by(
        user_id=current_user.id, conversation_id=conversation_id).first_or_404()
    
    # Delete all messages in the conversation
    ChatbotMessage.query.filter_by(conversation_id=conversation.id).delete()
    
    # Delete the conversation
    db.session.delete(conversation)
    db.session.commit()
    
    flash('Conversation has been deleted', 'success')
    return redirect(url_for('chat.history'))
