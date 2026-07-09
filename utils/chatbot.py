import re
import random
import logging
from utils.sentiment import analyze_sentiment, get_sentiment_category

# Define chatbot responses based on patterns and keywords
responses = {
    'greeting': [
        "Hello! I'm here to provide support and resources for your mental health journey.",
        "Hi there! How can I help with your mental wellbeing today?",
        "Welcome to the Mental Health Support Platform. How are you feeling today?"
    ],
    'goodbye': [
        "Take care of yourself. Remember, we're here whenever you need support.",
        "Goodbye! Don't hesitate to return if you need more support.",
        "Wishing you well. Come back anytime you need to talk."
    ],
    'thanks': [
        "You're welcome! I'm here to help.",
        "Glad I could be of assistance!",
        "It's my pleasure to support you on your journey."
    ],
    'feeling_bad': [
        "I'm sorry to hear you're feeling that way. Would you like to discuss some coping strategies?",
        "That sounds difficult. Remember that it's okay to not be okay sometimes. Would you like some resources that might help?",
        "I understand, and I'm here to listen. Have you considered tracking your mood in our mood tracker to monitor patterns?"
    ],
    'feeling_good': [
        "That's wonderful to hear! It's important to acknowledge and celebrate positive feelings.",
        "I'm glad you're feeling good! What's contributing to your positive mood today?",
        "That's great! Would you like to record this in your mood tracker to help identify what contributes to your wellbeing?"
    ],
    'anxiety': [
        "Anxiety can be challenging. Have you tried deep breathing exercises? They can help reduce anxiety in the moment.",
        "For anxiety, many find our guided meditation exercises helpful. Would you like to try one?",
        "When dealing with anxiety, grounding techniques can be useful. Would you like me to suggest some simple ones?"
    ],
    'depression': [
        "Depression can make everything feel more difficult. Have you reached out to any of our verified experts?",
        "I'm sorry you're experiencing depression. Regular physical activity, even small amounts, can sometimes help improve mood. Would you like some gentle exercise suggestions?",
        "Depression is a serious condition. While I can offer resources, it's important to seek professional help if you haven't already."
    ],
    'stress': [
        "Stress management is crucial for mental health. Our mindfulness exercises might help you find some relief.",
        "When stressed, taking short breaks throughout the day to reset can be beneficial. Would you like some quick stress-relief techniques?",
        "Stress can build up over time. Have you tried journaling about your stressors? Our journal feature can be a helpful outlet."
    ],
    'sleep': [
        "Good sleep is essential for mental health. Have you established a consistent sleep routine?",
        "Our mindfulness section has relaxation exercises that many find helpful for improving sleep quality.",
        "Difficulty sleeping is common with many mental health conditions. Would you like some tips for better sleep hygiene?"
    ],
    'help': [
        "I'm here to help! I can provide information about anxiety, depression, stress management, and more. What would you like to know about?",
        "I can assist with resources for mental health, recommend coping strategies, or point you to our forum where you can connect with others. How can I help specifically?",
        "You can ask me about our platform features, mental health resources, or coping strategies. What do you need assistance with?"
    ],
    'resources': [
        "Our platform offers a mood tracker, journal, meditation timer, and expert Q&A sessions. Would you like more information about any of these?",
        "We have mindfulness exercises, a supportive community forum, and verified mental health experts. Which resource interests you most?",
        "For immediate support, our forum is a great place to connect with others. For longer-term tools, consider our mood tracker and journal features."
    ],
    'meditation': [
        "Meditation can be a powerful tool for mental wellbeing. Have you tried our meditation timer in the mindfulness section?",
        "Even a few minutes of meditation daily can help reduce stress and improve focus. Would you like some beginner meditation tips?",
        "Our platform offers guided meditations for different purposes - stress relief, better sleep, and improved focus. Would you like to try one?"
    ],
    'community': [
        "Our community forum is a safe space to connect with others on similar journeys. You can share experiences or just read others' stories.",
        "Community support can be invaluable. Our forum has different categories for various mental health topics.",
        "Many users find comfort in knowing they're not alone. Our forum moderators ensure the community remains supportive and respectful."
    ],
    'experts': [
        "We have verified mental health experts who host regular Q&A sessions. You can view upcoming sessions in the experts section.",
        "Our experts specialize in various areas including anxiety, depression, stress management, and more. Would you like to see who's available?",
        "While our chatbot provides general guidance, our verified experts can offer more personalized insights during Q&A sessions."
    ],
    'default': [
        "I'm not sure I understand. Could you rephrase your question?",
        "I want to help, but I'm having trouble understanding. Could you try asking in a different way?",
        "I'm still learning and might not have the answer to that. Would you like to explore our resources or community forum instead?"
    ]
}

# Define patterns to match user input
patterns = {
    'greeting': r'\b(hi|hello|hey|greetings|howdy|hi there)\b',
    'goodbye': r'\b(bye|goodbye|see you|farewell|exit|quit)\b',
    'thanks': r'\b(thanks|thank you|appreciate it|grateful)\b',
    'feeling_bad': r'\b(sad|depressed|unhappy|miserable|awful|terrible|bad|down|low|upset|stressed|anxious|worried|afraid|scared)\b',
    'feeling_good': r'\b(happy|good|great|excellent|wonderful|amazing|fantastic|positive|joyful|excited|content|peaceful)\b',
    'anxiety': r'\b(anxiety|anxious|panic|worry|worried|fear|nervous|tension|stressed)\b',
    'depression': r'\b(depression|depressed|hopeless|despair|worthless|empty|numb)\b',
    'stress': r'\b(stress|stressed|overwhelmed|pressure|burnout|overload)\b',
    'sleep': r'\b(sleep|insomnia|tired|fatigue|exhausted|rest|restless)\b',
    'help': r'\b(help|assist|guidance|support|advice)\b',
    'resources': r'\b(resources|tools|features|services|options)\b',
    'meditation': r'\b(meditation|meditate|mindfulness|breathing|relax|calm)\b',
    'community': r'\b(community|forum|group|connect|share|others|members)\b',
    'experts': r'\b(expert|professional|therapist|psychologist|psychiatrist|counselor|doctor)\b'
}

def get_chatbot_response(user_message, user):
    """
    Generate a chatbot response based on user message patterns.
    
    Args:
        user_message (str): The message from the user
        user: The current user object (could be Anonymous)
        
    Returns:
        str: The chatbot's response
    """
    # Convert to lowercase for pattern matching
    message = user_message.lower()
    
    # Analyze sentiment
    sentiment_score = analyze_sentiment(message)
    sentiment_category = get_sentiment_category(sentiment_score)
    
    logging.debug(f"Message sentiment: {sentiment_category} ({sentiment_score})")
    
    # Check for emergency keywords
    emergency_pattern = r'\b(suicide|suicidal|kill myself|end my life|hurt myself|self harm|die)\b'
    if re.search(emergency_pattern, message):
        return ("I'm concerned about what you've shared. If you're having thoughts of harming yourself, "
                "please reach out to a crisis helpline immediately: National Suicide Prevention Lifeline "
                "at 1-800-273-8255 or text HOME to 741741 to reach the Crisis Text Line. These services "
                "are free, confidential, and available 24/7. Would you like me to provide more resources?")
    
    # Check for matches in our patterns
    for category, pattern in patterns.items():
        if re.search(pattern, message):
            return random.choice(responses[category])
    
    # Default response if no pattern matches
    return random.choice(responses['default'])
