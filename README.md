# MindfulConnect - Mental Health Support Platform

MindfulConnect is an anonymous mental health support platform with community forums, mood tracking, mindfulness exercises, and expert guidance.

## Features

- **Anonymous Community Forums**: Engage in discussions about mental health topics
- **Mood Tracking**: Track your mood patterns and emotional well-being over time
- **Journaling**: Express your thoughts in a private digital journal
- **Mindfulness Resources**: Access meditation timers, breathing exercises, and mindfulness practices
- **Expert Support**: Participate in Q&A sessions with verified mental health professionals
- **Support Chatbot**: Get basic mental health guidance through our rule-based chatbot

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (latest version recommended)
- pip

### Database Setup

1. Make sure PostgreSQL is installed and running on your system
2. Run the database setup script:

```bash
python local_db_setup.py
```

This script will:
- Create a PostgreSQL database for MindfulConnect
- Set up all necessary tables based on the schema
- Create a `.env` file with connection details

### Installing Dependencies

1. Clone this repository:
```bash
git clone <repository-url>
cd mindfulconnect
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up NLTK for sentiment analysis:
```bash
python setup_nltk.py
```

### Running the Application

1. Make sure your database is set up and running
2. Start the application with:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```
3. Access the application at `http://localhost:5000`

## Project Structure

```
├── app.py              # Application initialization
├── chatbot.py          # Rule-based mental health chatbot
├── forms.py            # Form definitions using Flask-WTF
├── main.py             # Main entry point
├── models.py           # Database models using SQLAlchemy
├── routes/             # Route handlers organized by feature
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── chatbot.py
│   ├── expert.py
│   ├── experts.py
│   ├── forum.py
│   ├── mindfulness.py
│   ├── mood.py
│   └── profile.py
├── static/             # Static assets
│   ├── css/
│   └── js/
├── templates/          # HTML templates
│   ├── auth/
│   ├── chatbot/
│   ├── experts/
│   ├── forum/
│   ├── mindfulness/
│   ├── mood/
│   └── profile/
└── utils/              # Utility functions
    ├── __init__.py
    ├── chatbot.py
    ├── sentiment.py
    └── helpers.py
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DATABASE_URL=postgresql://username:password@localhost:5432/mindfulconnect
PGDATABASE=mindfulconnect
PGUSER=your_db_username
PGPASSWORD=your_db_password
PGHOST=localhost
PGPORT=5432
SESSION_SECRET=your_secret_key_here
```
