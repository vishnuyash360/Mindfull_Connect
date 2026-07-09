import random
import string
import uuid
from datetime import datetime

def generate_anonymous_username():
    """Generate a random anonymous username."""
    adjectives = [
        "Calm", "Peaceful", "Serene", "Gentle", "Tranquil", 
        "Mindful", "Kind", "Caring", "Hopeful", "Brave",
        "Steady", "Patient", "Graceful", "Balanced", "Resilient"
    ]
    
    nouns = [
        "Journey", "Path", "River", "Mountain", "Ocean", 
        "Forest", "Meadow", "Garden", "Horizon", "Sky",
        "Star", "Sunset", "Breeze", "Whisper", "Harmony"
    ]
    
    # Generate a random adjective-noun pair with a random number
    random_number = random.randint(100, 999)
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random_number}"

def format_datetime(dt):
    """Format a datetime object for display."""
    if not dt:
        return ""
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        # Within the same day
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

def truncate_text(text, max_length=100):
    """Truncate text to a maximum length and add ellipsis if needed."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def calculate_reading_time(text):
    """Calculate the estimated reading time in minutes."""
    if not text:
        return 1
    
    # Average reading speed is about 200-250 words per minute
    word_count = len(text.split())
    minutes = max(1, round(word_count / 200))
    
    return minutes

def generate_unique_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())

def is_valid_email(email):
    """Simple email validation."""
    if not email or '@' not in email or '.' not in email:
        return False
    
    return True

def sanitize_html(text):
    """Very basic HTML sanitization."""
    if not text:
        return ""
    
    # Replace angle brackets with HTML entities
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    return sanitized
