import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download NLTK resources (if not already downloaded)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.
    Returns a float between -1.0 (very negative) and 1.0 (very positive).
    """
    if not text:
        return 0.0
    
    # Get polarity scores
    sentiment = sia.polarity_scores(text)
    
    # Return the compound score
    return sentiment['compound']

def get_sentiment_category(score):
    """
    Convert a sentiment score to a category.
    Returns 'negative', 'neutral', or 'positive'.
    """
    if score <= -0.05:
        return 'negative'
    elif score >= 0.05:
        return 'positive'
    else:
        return 'neutral'

def detect_concerning_content(text, threshold=-0.7):
    """
    Detect if content is highly negative, which might indicate 
    concerning mental health issues.
    Returns True if content is concerning, False otherwise.
    """
    sentiment_score = analyze_sentiment(text)
    return sentiment_score <= threshold

def get_concerning_keywords():
    """
    Returns a list of keywords that might indicate mental health crises.
    """
    return [
        'suicide', 'kill myself', 'die', 'end my life', 'no reason to live',
        'better off dead', 'can\'t go on', 'self harm', 'hurt myself',
        'hopeless', 'worthless', 'no point', 'no hope', 'no future'
    ]

def contains_concerning_keywords(text):
    """
    Check if text contains any concerning keywords.
    Returns True if any keyword is found, False otherwise.
    """
    if not text:
        return False
    
    text = text.lower()
    keywords = get_concerning_keywords()
    
    for keyword in keywords:
        if keyword in text:
            return True
    
    return False
