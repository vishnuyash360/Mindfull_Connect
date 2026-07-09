
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    display_name VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Forum Topics Table
CREATE TABLE IF NOT EXISTS forum_topic (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES "user"(id),
    category VARCHAR(50) NOT NULL,
    views INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    sentiment_score FLOAT
);

-- Forum Posts Table
CREATE TABLE IF NOT EXISTS forum_post (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES "user"(id),
    topic_id INTEGER REFERENCES forum_topic(id) ON DELETE CASCADE,
    is_solution BOOLEAN DEFAULT FALSE,
    sentiment_score FLOAT
);

-- Mood Entries Table
CREATE TABLE IF NOT EXISTS mood_entry (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    mood_level INTEGER NOT NULL CHECK (mood_level BETWEEN 1 AND 10),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags VARCHAR(255)
);

-- Journal Entries Table
CREATE TABLE IF NOT EXISTS journal (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_private BOOLEAN DEFAULT TRUE,
    sentiment_score FLOAT
);

-- Expert Profiles Table
CREATE TABLE IF NOT EXISTS expert (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE UNIQUE,
    credentials TEXT NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    bio TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP
);

-- Q&A Sessions Table
CREATE TABLE IF NOT EXISTS qa_session (
    id SERIAL PRIMARY KEY,
    expert_id INTEGER REFERENCES expert(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    max_participants INTEGER DEFAULT 20,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Q&A Session Participants Table
CREATE TABLE IF NOT EXISTS qa_participants (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES qa_session(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);

-- Q&A Questions Table
CREATE TABLE IF NOT EXISTS qa_question (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES qa_session(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT FALSE,
    upvotes INTEGER DEFAULT 0,
    is_answered BOOLEAN DEFAULT FALSE
);

-- Reports Table
CREATE TABLE IF NOT EXISTS report (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES forum_post(id) ON DELETE CASCADE,
    reporter_id INTEGER REFERENCES "user"(id),
    reason VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES "user"(id)
);

-- Forum Categories Table
CREATE TABLE IF NOT EXISTS forum_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forum Comments (Replies to Posts) Table
CREATE TABLE IF NOT EXISTS forum_comment (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES forum_post(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT FALSE,
    sentiment_score FLOAT
);

-- Expert Verification Requests Table
CREATE TABLE IF NOT EXISTS expert_verification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE UNIQUE,
    credentials TEXT NOT NULL,
    license_number VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    reviewed_by INTEGER REFERENCES "user"(id),
    reviewed_at TIMESTAMP,
    notes TEXT
);

-- Add some initial forum categories
INSERT INTO forum_category (name, description, slug, icon, display_order) VALUES
('General Discussion', 'General conversations about mental health and wellbeing', 'general', 'far fa-comments', 1),
('Anxiety', 'Discussions related to anxiety and stress management', 'anxiety', 'fas fa-brain', 2),
('Depression', 'Support and discussions about depression', 'depression', 'fas fa-cloud-rain', 3),
('Mindfulness', 'Sharing mindfulness practices and experiences', 'mindfulness', 'fas fa-leaf', 4),
('Self-Care', 'Tips and discussions about self-care routines', 'self-care', 'fas fa-heart', 5),
('Relationships', 'Discussing mental health in relationships', 'relationships', 'fas fa-users', 6)
ON CONFLICT (slug) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_forum_topic_user_id ON forum_topic(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_post_topic_id ON forum_post(topic_id);
CREATE INDEX IF NOT EXISTS idx_forum_post_user_id ON forum_post(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_entry_user_id ON mood_entry(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_user_id ON journal(user_id);
CREATE INDEX IF NOT EXISTS idx_qa_session_expert_id ON qa_session(expert_id);
CREATE INDEX IF NOT EXISTS idx_qa_question_session_id ON qa_question(session_id);
CREATE INDEX IF NOT EXISTS idx_report_post_id ON report(post_id);