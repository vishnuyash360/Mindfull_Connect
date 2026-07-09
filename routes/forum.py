from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import ForumTopic, ForumPost, Report
from utils.sentiment import analyze_sentiment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from demo import db
forum_bp = Blueprint('forum', __name__, url_prefix='/forum')

class TopicForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=255)])
    category = SelectField('Category', choices=[
        ('general', 'General Discussion'),
        ('anxiety', 'Anxiety'),
        ('depression', 'Depression'),
        ('stress', 'Stress Management'),
        ('relationships', 'Relationships'),
        ('self-care', 'Self-Care'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=20, max=10000)])
    submit = SubmitField('Create Topic')

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=5, max=5000)])
    submit = SubmitField('Post Reply')

class ReportForm(FlaskForm):
    reason = SelectField('Reason', choices=[
        ('inappropriate', 'Inappropriate Content'),
        ('harmful', 'Harmful or Dangerous'),
        ('spam', 'Spam'),
        ('offensive', 'Offensive Language'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    details = TextAreaField('Details', validators=[Length(max=1000)])
    submit = SubmitField('Submit Report')

@forum_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    # Base query
    query = ForumTopic.query
    
    # Apply category filter if provided
    if category:
        query = query.filter_by(category=category)
    
    # Get pinned topics first, then sort by updated_at
    pinned_topics = query.filter_by(is_pinned=True).order_by(ForumTopic.updated_at.desc()).all()
    regular_topics = query.filter_by(is_pinned=False).order_by(ForumTopic.updated_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('forum/index.html', 
                          title='Community Forum', 
                          pinned_topics=pinned_topics,
                          topics=regular_topics,
                          category=category)

@forum_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_topic():
    form = TopicForm()
    if form.validate_on_submit():
        topic = ForumTopic(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id
        )
        
        # Analyze sentiment of the topic content
        sentiment_score = analyze_sentiment(form.content.data)
        topic.sentiment_score = sentiment_score
        
        db.session.add(topic)
        db.session.commit()
        
        flash('Your topic has been created!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=topic.id))
    
    return render_template('forum/post.html', title='Create Topic', form=form, is_topic=True)

@forum_bp.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    posts = ForumPost.query.filter_by(topic_id=topic_id).order_by(ForumPost.created_at).all()
    
    # Increment view count
    topic.views += 1
    db.session.commit()
    
    form = PostForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to be logged in to reply to topics.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        
        if topic.is_closed:
            flash('This topic is closed and no longer accepting replies.', 'warning')
            return redirect(url_for('forum.view_topic', topic_id=topic_id))
        
        post = ForumPost(
            content=form.content.data,
            user_id=current_user.id,
            topic_id=topic_id
        )
        
        # Analyze sentiment of the post content
        sentiment_score = analyze_sentiment(form.content.data)
        post.sentiment_score = sentiment_score
        
        db.session.add(post)
        db.session.commit()
        
        # Update the topic's updated_at time
        topic.updated_at = post.created_at
        db.session.commit()
        
        flash('Your reply has been posted!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=topic_id))
    
    return render_template('forum/topic.html', 
                          title=topic.title, 
                          topic=topic, 
                          posts=posts, 
                          form=form)

@forum_bp.route('/post/<int:post_id>/report', methods=['GET', 'POST'])
@login_required
def report_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    form = ReportForm()
    
    if form.validate_on_submit():
        report = Report(
            post_id=post_id,
            reporter_id=current_user.id,
            reason=form.reason.data,
            details=form.details.data
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Your report has been submitted. A moderator will review it shortly.', 'success')
        return redirect(url_for('forum.view_topic', topic_id=post.topic_id))
    
    return render_template('forum/report.html', title='Report Post', form=form, post=post)

@forum_bp.route('/topic/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    
    # Check if the current user is the author or an admin
    if topic.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = TopicForm()
    
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.content = form.content.data
        topic.category = form.category.data
        
        # Re-analyze sentiment if content changed
        sentiment_score = analyze_sentiment(form.content.data)
        topic.sentiment_score = sentiment_score
        
        db.session.commit()
        
        flash('Your topic has been updated!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=topic.id))
    
    elif request.method == 'GET':
        form.title.data = topic.title
        form.content.data = topic.content
        form.category.data = topic.category
    
    return render_template('forum/post.html', 
                          title='Edit Topic', 
                          form=form, 
                          is_topic=True, 
                          is_edit=True)

@forum_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    
    # Check if the current user is the author or an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = PostForm()
    
    if form.validate_on_submit():
        post.content = form.content.data
        
        # Re-analyze sentiment
        sentiment_score = analyze_sentiment(form.content.data)
        post.sentiment_score = sentiment_score
        
        db.session.commit()
        
        flash('Your post has been updated!', 'success')
        return redirect(url_for('forum.view_topic', topic_id=post.topic_id))
    
    elif request.method == 'GET':
        form.content.data = post.content
    
    return render_template('forum/post.html', 
                          title='Edit Reply', 
                          form=form, 
                          is_topic=False, 
                          is_edit=True)
