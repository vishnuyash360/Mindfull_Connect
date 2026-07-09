import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    logger.info("Downloading NLTK vader_lexicon for sentiment analysis")
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
    def analyze_text(self, text):
        """
        Analyze the sentiment of the provided text.
        Returns a score between -1 (very negative) and 1 (very positive).
        """
        if not text:
            return 0
            
        try:
            scores = self.analyzer.polarity_scores(text)
            return scores['compound']  # compound score is a normalized score between -1 and 1
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0
            
    def get_sentiment_category(self, score):
        """
        Converts numerical sentiment score to a category.
        """
        if score <= -0.5:
            return "very negative"
        elif score <= -0.1:
            return "negative"
        elif score < 0.1:
            return "neutral"
        elif score < 0.5:
            return "positive"
        else:
            return "very positive"
            
    def should_flag_content(self, text):
        """
        Determines if content should be flagged for moderator review
        based on extremely negative sentiment or concerning content.
        """
        score = self.analyze_text(text)
        
        # Flag very negative content for review
        if score <= -0.7:
            return True
            
        # Check for concerning keywords in the text
        concerning_keywords = [
            "suicide", "kill myself", "end my life", "self harm",
            "cutting myself", "hurt myself", "no reason to live"
        ]
        
        text_lower = text.lower()
        for keyword in concerning_keywords:
            if keyword in text_lower:
                return True
                
        return False

# Initialize the sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()
