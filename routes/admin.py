from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from datetime import datetime
from models import User, Expert
from app import db
from models import User, ForumPost, Report

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Ensure only admin users can access admin routes."""
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
@login_required
def dashboard():
    """Display the admin dashboard."""
    # Get counts for various entities
    user_count = User.query.count()
    expert_count = User.query.filter_by(is_expert=True).count()
    post_count = ForumPost.query.count()
    pending_reports_count = Report.query.filter_by(status="pending").count()
    # No verification_status field in User model; set to 0 for now
    pending_verifications_count = 0
    
    return render_template(
        'admin_dashboard.html',
        user_count=user_count,
        expert_count=expert_count,
        post_count=post_count,
        pending_reports_count=pending_reports_count,
        pending_verifications_count=pending_verifications_count
    )

@admin_bp.route('/experts', methods=['GET', 'POST'])
@login_required
def manage_experts():
    """List and verify/unverify experts."""
    from flask import request, redirect, url_for

    users = User.query.join(Expert).all()

    if request.method == "POST":
        user_id = int(request.form.get('user_id'))
        action = request.form.get('action')

        user = User.query.get_or_404(user_id)
        expert = user.expert_profile  # relationship

        if not expert:
            abort(404)

        if action == "verify":
            expert.is_verified = True
            user.role = 'expert'      # ✅ optional but recommended

        elif action == "unverify":
            expert.is_verified = False
            user.role = 'user'

        db.session.commit()
        return redirect(url_for('admin.manage_experts'))

    return render_template('admin_experts.html', users=users)


@admin_bp.route('/users')
@login_required
def users():
    """Manage users."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.username.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    
    users = query.order_by(User.registration_date.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin_dashboard.html', users=users, search=search, section='users')

@admin_bp.route('/experts')
@login_required
def experts():
    """Manage expert verifications."""
    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    
    # No verification_status. Filter by is_expert for now.
    experts = User.query.filter_by(is_expert=True).order_by(User.id.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin_dashboard.html', experts=experts, status=status, section='experts')

@admin_bp.route('/expert/<int:user_id>', methods=['GET', 'POST'])
@login_required
def expert_details(user_id):
    """View and manage expert verification details."""
    user = User.query.get_or_404(user_id)
    expert_details = user.expert_profile
    if not expert_details:
        abort(404)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'approve':
            user.is_expert = True
            expert_details.verification_date = datetime.utcnow()
            db.session.commit()
            flash(f'Expert verification for {user.username} has been approved', 'success')
        
        elif action == 'reject':
            db.session.commit()
            flash(f'Expert verification for {user.username} has been rejected', 'info')
        
        return redirect(url_for('admin.experts'))
    
    return render_template('admin_dashboard.html', 
                          user=user, 
                          expert_details=expert_details, 
                          section='expert_details')

@admin_bp.route('/reports')
@login_required
def reports():
    """Manage reported content."""
    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    
    query = Report.query.filter_by(status=status)
    reports = query.order_by(Report.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin_dashboard.html', reports=reports, status=status, section='reports')

@admin_bp.route('/report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def report_details(report_id):
    """Review a specific report."""
    report = Report.query.get_or_404(report_id)
    
    # Get reported content
    reported_content = None
    if report.reported_content_type == 'post':
        reported_content = ForumPost.query.get(report.reported_content_id)
    elif report.reported_content_type == 'comment':
        reported_content = None  # ForumComment model does not exist
    elif report.reported_content_type == 'user':
        reported_content = User.query.get(report.reported_content_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        action_taken = request.form.get('action_taken')
        
        report.status = "reviewed"
        report.reviewed_by = current_user.id
        report.reviewed_at = datetime.utcnow()
        report.action_taken = action_taken
        
        if action == 'hide_content' and reported_content:
            if hasattr(reported_content, 'is_hidden'):
                reported_content.is_hidden = True
        
        db.session.commit()
        flash('Report has been processed', 'success')
        return redirect(url_for('admin.reports'))
    
    return render_template('admin_dashboard.html', 
                          report=report, 
                          reported_content=reported_content, 
                          section='report_details')

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    """Manage forum categories."""
    return "Category management not implemented", 501

@admin_bp.route('/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit a forum category."""
    return "Edit category not implemented", 501

@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a forum category."""
    return "Delete category not implemented", 501
