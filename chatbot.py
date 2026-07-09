import re
import random
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download NLTK data for tokenization and lemmatization
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')

class MentalHealthChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.greeting_patterns = [
            r"hi|hello|hey",
            r"how are you",
            r"what's up",
            r"good (morning|afternoon|evening)"
        ]
        
        self.crisis_patterns = [
            r"suicid(e|al)",
            r"kill (myself|me)",
            r"want to (die|end it)",
            r"harm(ing)? myself",
            r"no reason to live"
        ]
        
        self.anxiety_patterns = [
            r"anxious|anxiety|panic",
            r"worry(ing)? (too much|constantly|always)",
            r"can't (stop|control) worrying",
            r"nervous|restless|tense"
        ]
        
        self.depression_patterns = [
            r"depress(ed|ion)",
            r"sad|down|blue",
            r"no (interest|pleasure)",
            r"hopeless|worthless",
            r"tired|exhausted|fatigue"
        ]
        
        self.sleep_patterns = [
            r"(can't|trouble|difficulty) sleep(ing)?",
            r"insomnia",
            r"(poor|bad) sleep",
            r"sleep (too much|a lot)"
        ]
        
        self.general_help_patterns = [
            r"help|advice",
            r"need (support|guidance)",
            r"don't know what to do",
            r"resources|tools"
        ]

        self.reflection_patterns = [
            r"feel(ing)?",
            r"think(ing)?",
            r"believe",
            r"want"
        ]
        
    def _preprocess(self, message):
        # Tokenize and lemmatize the message
        tokens = word_tokenize(message.lower())
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def _check_pattern_match(self, message, patterns):
        for pattern in patterns:
            if re.search(pattern, message.lower()):
                return True
        return False
    
    def _create_reflection(self, message):
        # Create a simple reflection by changing pronouns
        message = message.lower()
        message = re.sub(r'\bi\b', 'you', message)
        message = re.sub(r'\bmy\b', 'your', message)
        message = re.sub(r'\bme\b', 'you', message)
        message = re.sub(r'\bam\b', 'are', message)
        
        for pattern in self.reflection_patterns:
            if re.search(pattern, message):
                return f"It sounds like {message}. Would you like to talk more about that?"
        
        return None

    def get_response(self, message):
        if not message.strip():
            return "I didn't catch that. Could you please say something?"
            
        if self._check_pattern_match(message, self.greeting_patterns):
            return random.choice([
                "Hello! I'm here to support you. How are you feeling today?",
                "Hi there! How can I help you today?",
                "Hello! I'm your mental health chatbot. What's on your mind?",
                "Greetings! How are you doing today?"
            ])
            
        if self._check_pattern_match(message, self.crisis_patterns):
            return (
                "I'm concerned about what you've shared. If you're in crisis, please reach out to a crisis hotline immediately: "
                "National Suicide Prevention Lifeline: 988 or 1-800-273-8255. "
                "Would you like me to provide more crisis resources?"
            )
            
        if self._check_pattern_match(message, self.anxiety_patterns):
            return random.choice([
                "It sounds like you're experiencing anxiety. Have you tried any breathing exercises or grounding techniques?",
                "Anxiety can be really challenging. Would you like me to share some coping strategies for anxiety?",
                "I hear that you're feeling anxious. Sometimes focusing on your breath can help. Would you like me to guide you through a quick breathing exercise?",
                "Dealing with anxiety is difficult. Have you spoken with a mental health professional about these feelings?"
            ])
            
        if self._check_pattern_match(message, self.depression_patterns):
            return random.choice([
                "I'm sorry to hear you're feeling down. Depression can be really tough. Have you been able to talk to anyone about how you're feeling?",
                "It sounds like you might be experiencing symptoms of depression. Have you considered reaching out to a mental health professional?",
                "When we're feeling depressed, even small self-care activities can help. Could you think of one small thing you might do today to take care of yourself?",
                "Depression can make everything feel harder. Would you like me to share some resources that might help?"
            ])
            
        if self._check_pattern_match(message, self.sleep_patterns):
            return random.choice([
                "Sleep problems can be really frustrating. Have you tried establishing a consistent sleep routine?",
                "Difficulty sleeping can affect your mental health. Some people find that limiting screen time before bed helps. Have you tried that?",
                "Sleep issues are common with many mental health conditions. Would you like some tips for better sleep hygiene?",
                "Getting quality sleep is important for mental health. Have you spoken with a healthcare provider about your sleep concerns?"
            ])
            
        if self._check_pattern_match(message, self.general_help_patterns):
            return random.choice([
                "I'm here to support you. Could you tell me more about what you're going through?",
                "I'd be happy to help. What specific kind of support are you looking for?",
                "There are many resources available on this platform. Would you like to explore the forums, mood tracking, or meditation guides?",
                "Sometimes talking to others who understand can help. Have you considered joining one of our community forums?"
            ])
            
        # Try to create a reflection
        reflection = self._create_reflection(message)
        if reflection:
            return reflection
            
        # Default responses if no patterns match
        return random.choice([
            "I hear you. Could you tell me more about that?",
            "Thank you for sharing. How does that make you feel?",
            "I'm listening. What else would you like to share?",
            "I understand this might be difficult to talk about. Take your time.",
            "Would you like to explore some coping strategies together?",
            "Have you talked to anyone else about this?",
            "How can I best support you right now?"
        ])

# Initialize the chatbot
chatbot = MentalHealthChatbot()
