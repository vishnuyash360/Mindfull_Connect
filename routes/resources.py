from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

resources = Blueprint('resources', __name__, url_prefix='/resources')

@resources.route('/meditation')
def meditation():
    return render_template('resources/meditation.html', title='Meditation Timer')

@resources.route('/mindfulness')
def mindfulness():
    # List of mindfulness exercises
    exercises = [
        {
            'title': '5-4-3-2-1 Grounding Exercise',
            'description': 'A technique to ground yourself when feeling anxious or overwhelmed.',
            'steps': [
                'Acknowledge 5 things you see around you',
                'Acknowledge 4 things you can touch around you',
                'Acknowledge 3 things you hear',
                'Acknowledge 2 things you can smell',
                'Acknowledge 1 thing you can taste'
            ]
        },
        {
            'title': 'Body Scan Meditation',
            'description': 'A technique to develop awareness of your body and release tension.',
            'steps': [
                'Find a comfortable position sitting or lying down',
                'Close your eyes and take several deep breaths',
                'Bring attention to your feet and notice any sensations',
                'Slowly scan upward through your body, noticing sensations in each part',
                'When you reach your head, take a moment to notice how your entire body feels'
            ]
        },
        {
            'title': 'Mindful Breathing',
            'description': 'A simple technique to anchor yourself in the present moment.',
            'steps': [
                'Find a comfortable seated position',
                'Close your eyes or maintain a soft gaze',
                'Breathe naturally and focus on the sensation of breath',
                'When your mind wanders, gently bring attention back to your breath',
                'Continue for 5-10 minutes'
            ]
        },
        {
            'title': 'Loving-Kindness Meditation',
            'description': 'Cultivate feelings of goodwill, kindness, and warmth towards yourself and others.',
            'steps': [
                'Sit comfortably and take a few deep breaths',
                'Bring to mind someone you care about and repeat phrases like "May you be happy, may you be healthy..."',
                'Direct these phrases toward yourself',
                'Extend these wishes to others, including difficult people',
                'Finally, extend these wishes to all beings everywhere'
            ]
        }
    ]
    
    return render_template('resources/mindfulness.html', 
                          title='Mindfulness Exercises',
                          exercises=exercises)

@resources.route('/crisis-resources')
def crisis_resources():
    # List of crisis resources
    resources_list = [
        {
            'name': 'National Suicide Prevention Lifeline',
            'contact': '988 or 1-800-273-8255',
            'website': 'https://suicidepreventionlifeline.org/',
            'description': 'A national network of local crisis centers that provides free and confidential emotional support to people in suicidal crisis or emotional distress 24/7.'
        },
        {
            'name': 'Crisis Text Line',
            'contact': 'Text HOME to 741741',
            'website': 'https://www.crisistextline.org/',
            'description': 'Connect with a trained crisis counselor to receive free, 24/7 crisis support via text message.'
        },
        {
            'name': 'SAMHSA National Helpline',
            'contact': '1-800-662-4357',
            'website': 'https://www.samhsa.gov/find-help/national-helpline',
            'description': 'A confidential, free, 24/7/365 information service for individuals and family members facing mental and/or substance use disorders.'
        },
        {
            'name': 'The Trevor Project',
            'contact': '1-866-488-7386',
            'website': 'https://www.thetrevorproject.org/',
            'description': 'A national 24-hour, toll free confidential suicide hotline for LGBTQ youth.'
        },
        {
            'name': 'Veterans Crisis Line',
            'contact': '988 (Press 1) or 1-800-273-8255 (Press 1)',
            'website': 'https://www.veteranscrisisline.net/',
            'description': 'Connects veterans in crisis and their families and friends with qualified Department of Veterans Affairs responders.'
        }
    ]
    
    return render_template('resources/crisis.html',
                          title='Crisis Resources',
                          resources=resources_list)
