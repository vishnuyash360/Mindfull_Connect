import os
import logging
from flask import Flask
from demo import db
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from routes.mood import mood_bp



# Configure logging
logging.basicConfig(level=logging.DEBUG)


login_manager = LoginManager()
# Create the app
app = Flask(__name__)
app.secret_key = "a7485ef61035a52bf7fceb7e17b1d010f3356c9571221397a1ce7716cac1126a"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///default.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Register blueprints
with app.app_context():
    from models import User, Anonymous, ForumTopic, ForumPost, MoodEntry, Journal, Expert, QASession, Report
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.forum import forum_bp
    from routes.profile import profile_bp
    from routes.chatbot import chatbot_bp
    from routes.experts import experts_bp
    from routes.mindfulness import mindfulness_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(experts_bp)
    app.register_blueprint(mindfulness_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mood_bp)
    # Create all database tables
    db.create_all()
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Set Anonymous user
login_manager.anonymous_user = Anonymous

# Route for home page
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
