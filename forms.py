from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    display_name = StringField('Display Name (Optional)', validators=[Optional(), Length(max=64)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ExpertVerificationForm(FlaskForm):
    credentials = TextAreaField('Professional Credentials', validators=[DataRequired(), Length(min=10, max=500)])
    license_number = StringField('License Number', validators=[DataRequired(), Length(min=3, max=100)])
    specialty = StringField('Specialty Area', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Submit for Verification')

class NewTopicForm(FlaskForm):
    title = StringField('Topic Title', validators=[DataRequired(), Length(min=5, max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    content = TextAreaField('First Post', validators=[DataRequired(), Length(min=10)])
    anonymous = BooleanField('Post Anonymously')
    submit = SubmitField('Create Topic')

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    anonymous = BooleanField('Post Anonymously')
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=3)])
    anonymous = BooleanField('Comment Anonymously')
    submit = SubmitField('Submit')

class MoodEntryForm(FlaskForm):
    mood_score = IntegerField('How are you feeling today? (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Save')

class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Save')

class QASessionForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    scheduled_time = DateTimeField('Scheduled Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=15, max=180)])
    max_participants = IntegerField('Maximum Participants', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Create Session')

class QAQuestionForm(FlaskForm):
    content = TextAreaField('Question', validators=[DataRequired(), Length(min=5, max=1000)])
    anonymous = BooleanField('Ask Anonymously')
    submit = SubmitField('Submit Question')

class ReportForm(FlaskForm):
    content_type = HiddenField('Content Type', validators=[DataRequired()])
    content_id = HiddenField('Content ID', validators=[DataRequired()])
    reason = TextAreaField('Reason for Report', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Report')

class ChatbotForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send')
