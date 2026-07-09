import random
from utils.sentiment_analysis import get_sentiment_category, contains_concerning_keywords

# Dictionary of mental health topics and responses
topics = {
    "anxiety": [
        "Anxiety can feel overwhelming. Deep breathing exercises might help - try breathing in for 4 counts, holding for 2, and out for 6.",
        "When anxiety strikes, grounding techniques can help. Try naming 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
        "Regular physical activity, even just a short walk, can help reduce anxiety symptoms."
    ],
    "depression": [
        "Depression can make even small tasks feel difficult. Try breaking activities into smaller steps and celebrating each accomplishment.",
        "While it may be challenging, maintaining social connections can help when dealing with depression.",
        "Consider establishing a routine to provide structure to your day, which can be helpful when experiencing depression."
    ],
    "stress": [
        "Stress management is important for mental health. Activities like yoga, meditation, or even simple stretching can help.",
        "Taking short breaks throughout your day can help manage stress levels.",
        "Progressive muscle relaxation can help with stress - tighten and then release each muscle group in your body."
    ],
    "sleep": [
        "Creating a consistent sleep schedule can improve your mental well-being.",
        "Avoiding screens an hour before bed can help improve sleep quality.",
        "Creating a relaxing bedtime routine can signal to your body that it's time to sleep."
    ],
    "mindfulness": [
        "Mindfulness involves staying present in the moment. Try focusing on your breath when you notice your mind wandering.",
        "A simple mindfulness practice is to fully focus on everyday activities, like eating or walking.",
        "Regular mindfulness practice can help reduce stress and improve overall well-being."
    ],
    "meditation": [
        "Even just 5 minutes of meditation can help calm your mind.",
        "There are many styles of meditation - you might want to try different approaches to find what works for you.",
        "Guided meditations can be helpful when you're first starting a meditation practice."
    ],
    "self_care": [
        "Self-care is essential for mental health. This could include taking time for hobbies, setting boundaries, or getting enough rest.",
        "Physical self-care like nutrition, exercise, and sleep are foundations of mental well-being.",
        "Self-care looks different for everyone - it's about finding what helps you recharge."
    ]
}

# Greetings and general responses
greetings = [
    "Hello! I'm MindWell's support chatbot. How can I help with your mental health questions today?",
    "Hi there! I'm here to provide mental health information and resources. What would you like to talk about?",
    "Welcome to MindWell's chat support. I'm here to help with mental health questions. How are you feeling today?"
]

goodbyes = [
    "Take care of yourself. Remember, it's okay to reach out for help when needed.",
    "Wishing you well on your mental health journey. Feel free to return if you have more questions.",
    "Thank you for chatting. Remember to be kind to yourself today."
]

unknown_responses = [
    "I'm not sure I understand. Could you rephrase your question about mental health?",
    "I'd like to help, but I'm not sure what you're asking. Could you try asking in a different way?",
    "I'm still learning and may not have information on that topic. Could you ask about another mental health area?"
]

positive_reinforcement = [
    "It's great that you're taking steps to care for your mental health.",
    "Seeking information is a positive step toward mental well-being.",
    "You're doing something important by focusing on your mental health."
]

crisis_responses = [
    "It sounds like you might be going through a difficult time. Please remember that help is available. Consider calling a crisis hotline at 988 (US) or texting HOME to 741741 to speak with a crisis counselor.",
    "I'm concerned about what you've shared. Please consider reaching out to a mental health professional or calling a crisis line like 988 (US) for immediate support.",
    "If you're experiencing thoughts of harming yourself, please reach out for help immediately. You can call 988 or go to your nearest emergency room."
]

def get_chatbot_response(message, sentiment_score=None):
    """Generate a response based on the user's message."""
    message = message.lower()
    
    # Check for crisis keywords first
    if contains_concerning_keywords(message):
        return random.choice(crisis_responses)
    
    # Check for greetings
    if any(greeting in message for greeting in ["hello", "hi", "hey", "greetings"]):
        return random.choice(greetings)
    
    # Check for goodbyes
    if any(goodbye in message for goodbye in ["bye", "goodbye", "see you", "thanks", "thank you"]):
        return random.choice(goodbyes)
    
    # Check for specific mental health topics
    response_candidates = []
    
    if any(word in message for word in ["anxious", "anxiety", "nervous", "worry", "panic"]):
        response_candidates.extend(topics["anxiety"])
    
    if any(word in message for word in ["depressed", "depression", "sad", "hopeless", "unmotivated"]):
        response_candidates.extend(topics["depression"])
    
    if any(word in message for word in ["stress", "stressed", "overwhelmed", "pressure"]):
        response_candidates.extend(topics["stress"])
    
    if any(word in message for word in ["sleep", "insomnia", "tired", "rest", "awake"]):
        response_candidates.extend(topics["sleep"])
    
    if any(word in message for word in ["mindful", "mindfulness", "present", "awareness"]):
        response_candidates.extend(topics["mindfulness"])
    
    if any(word in message for word in ["meditate", "meditation", "relax", "calm"]):
        response_candidates.extend(topics["meditation"])
    
    if any(word in message for word in ["self-care", "selfcare", "self care", "care for myself"]):
        response_candidates.extend(topics["self_care"])
    
    # If we have response candidates, choose one randomly
    if response_candidates:
        response = random.choice(response_candidates)
        # Add positive reinforcement based on sentiment
        if sentiment_score and sentiment_score > 0.2:
            response = f"{random.choice(positive_reinforcement)} {response}"
        return response
    
    # If no specific topic was identified
    return random.choice(unknown_responses)
