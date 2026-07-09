from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from datetime import datetime
from sqlalchemy import desc

from models import ForumCategory, ForumTopic, ForumPost, ForumComment, Report
from forms import NewTopicForm, PostForm, CommentForm, ReportForm
from sentiment import sentiment_analyzer

forums = Blueprint('forums', __name__, url_prefix='/forums')

@forums.route('/')
def index():
    categories = ForumCategory.query.all()
    return render_template('forums/index.html', title='Forums', categories=categories)

@forums.route('/category/<int:id>')
def category(id):
    category = ForumCategory.query.get_or_404(id)
    topics = ForumTopic.query.filter_by(category_id=id).order_by(desc(ForumTopic.created_at)).all()
    return render_template('forums/category.html', title=category.name, category=category, topics=topics)

@forums.route('/new-topic', methods=['GET', 'POST'])
@login_required
def new_topic():
    form = NewTopicForm()
    form.category_id.choices = [(c.id, c.name) for c in ForumCategory.query.all()]
    
    if form.validate_on_submit():
        # Create a new topic
        topic = ForumTopic(
            title=form.title.data,
            category_id=form.category_id.data,
            created_by=current_user.id
        )
        
        db.session.add(topic)
        db.session.flush()  # Get the topic ID before committing
        
        # Create the first post in this topic
        sentiment_score = sentiment_analyzer.analyze_text(form.content.data)
        post = ForumPost(
            content=form.content.data,
            topic_id=topic.id,
            user_id=current_user.id,
            anonymous=form.anonymous.data,
            sentiment_score=sentiment_score
        )
        
        # Check if post needs moderation based on sentiment
        needs_moderation = sentiment_analyzer.should_flag_content(form.content.data)
        
        db.session.add(post)
        db.session.commit()
        
        if needs_moderation:
            flash('Your post has been flagged for review by moderators due to potentially concerning content.', 'warning')
        else:
            flash('New topic created successfully!', 'success')
            
        return redirect(url_for('forums.topic', id=topic.id))
    
    return render_template('forums/new_topic.html', title='Create New Topic', form=form)

@forums.route('/topic/<int:id>', methods=['GET', 'POST'])
def topic(id):
    topic = ForumTopic.query.get_or_404(id)
    posts = ForumPost.query.filter_by(topic_id=id).order_by(ForumPost.created_at).all()
    
    # Comment form for the main topic
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        sentiment_score = sentiment_analyzer.analyze_text(form.content.data)
        comment = ForumComment(
            content=form.content.data,
            post_id=posts[0].id,  # Comment on the first post (topic post)
            user_id=current_user.id,
            anonymous=form.anonymous.data,
            sentiment_score=sentiment_score
        )
        
        # Check if comment needs moderation
        needs_moderation = sentiment_analyzer.should_flag_content(form.content.data)
        
        db.session.add(comment)
        db.session.commit()
        
        if needs_moderation:
            flash('Your comment has been flagged for review by moderators due to potentially concerning content.', 'warning')
        else:
            flash('Your comment has been added!', 'success')
            
        return redirect(url_for('forums.topic', id=id))
    
    # Get report form
    report_form = ReportForm()
    
    return render_template('forums/topic.html', 
                          title=topic.title, 
                          topic=topic, 
                          posts=posts, 
                          form=form, 
                          report_form=report_form)

@forums.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = ForumPost.query.get_or_404(id)
    topic = ForumTopic.query.get_or_404(post.topic_id)
    comments = ForumComment.query.filter_by(post_id=id).order_by(ForumComment.created_at).all()
    
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        sentiment_score = sentiment_analyzer.analyze_text(form.content.data)
        comment = ForumComment(
            content=form.content.data,
            post_id=id,
            user_id=current_user.id,
            anonymous=form.anonymous.data,
            sentiment_score=sentiment_score
        )
        
        # Check if comment needs moderation
        needs_moderation = sentiment_analyzer.should_flag_content(form.content.data)
        
        db.session.add(comment)
        db.session.commit()
        
        if needs_moderation:
            flash('Your comment has been flagged for review by moderators due to potentially concerning content.', 'warning')
        else:
            flash('Your comment has been added!', 'success')
            
        return redirect(url_for('forums.post', id=id))
    
    # Get report form
    report_form = ReportForm()
    
    return render_template('forums/post.html', 
                          title=f"Reply to: {topic.title}", 
                          post=post, 
                          topic=topic, 
                          comments=comments, 
                          form=form,
                          report_form=report_form)

@forums.route('/report', methods=['POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            content_type=form.content_type.data,
            content_id=int(form.content_id.data),
            reason=form.reason.data
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Your report has been submitted for review. Thank you for helping keep our community safe.', 'success')
    else:
        flash('There was an error with your report. Please try again.', 'danger')
    
    # Redirect back to the page where the report was made
    return redirect(request.referrer or url_for('forums.index'))

@forums.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('index'))
    
    reports = Report.query.filter_by(status='pending').all()
    return render_template('forums/admin_reports.html', reports=reports)

@forums.route('/admin/report/<int:id>/<action>', methods=['POST'])
@login_required
def process_report(id, action):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('index'))
    
    report = Report.query.get_or_404(id)
    
    if action == 'dismiss':
        report.status = 'reviewed'
        report.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash('Report dismissed', 'info')
    
    elif action == 'remove_content':
        report.status = 'actioned'
        report.reviewed_at = datetime.utcnow()
        
        # Remove the reported content based on content_type
        if report.content_type == 'post':
            post = ForumPost.query.get(report.content_id)
            if post:
                db.session.delete(post)
        elif report.content_type == 'comment':
            comment = ForumComment.query.get(report.content_id)
            if comment:
                db.session.delete(comment)
        
        db.session.commit()
        flash('Content removed and report marked as actioned', 'success')
    
    return redirect(url_for('forums.admin_reports'))
