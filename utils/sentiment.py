import nltk
import logging
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data (if not already downloaded)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except Exception as e:
        logging.error(f"Failed to download NLTK data: {str(e)}")

# Initialize the sentiment analyzer
try:
    sid = SentimentIntensityAnalyzer()
except Exception as e:
    logging.error(f"Failed to initialize SentimentIntensityAnalyzer: {str(e)}")
    sid = None

def analyze_sentiment(text):
    """
    Analyze the sentiment of a text and return a score between -1 and 1,
    where -1 is very negative, 0 is neutral, and 1 is very positive.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        float: A sentiment score between -1 and 1
    """
    if not text or not sid:
        return 0.0
    
    try:
        # Get sentiment scores
        scores = sid.polarity_scores(text)
        
        # Return the compound score which is a normalized score between -1 and 1
        return scores['compound']
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {str(e)}")
        return 0.0

def get_sentiment_category(score):
    """
    Convert a numerical sentiment score to a category.
    
    Args:
        score (float): Sentiment score between -1 and 1
        
    Returns:
        str: Sentiment category (very negative, negative, neutral, positive, very positive)
    """
    if score <= -0.6:
        return "very negative"
    elif score <= -0.2:
        return "negative"
    elif score <= 0.2:
        return "neutral"
    elif score <= 0.6:
        return "positive"
    else:
        return "very positive"

def should_flag_content(text):
    """
    Determine if the content should be flagged for review based on sentiment.
    Flag very negative content for potential moderation.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        bool: True if the content should be flagged, False otherwise
    """
    score = analyze_sentiment(text)
    return score <= -0.7  # Flag very negative content
