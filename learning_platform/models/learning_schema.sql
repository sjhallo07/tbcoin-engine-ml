-- Learning Platform Database Schema
-- AI Learning Modules for Python Machine Learning

-- Users table for learner profiles
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    skill_level VARCHAR(20) DEFAULT 'beginner',
    preferred_library VARCHAR(50),
    learning_goals TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Learning modules table
CREATE TABLE IF NOT EXISTS learning_modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    library VARCHAR(50),
    prerequisites JSONB DEFAULT '[]',
    estimated_duration_minutes INTEGER DEFAULT 60,
    topics JSONB DEFAULT '[]',
    learning_objectives JSONB DEFAULT '[]',
    is_published BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    order_index INTEGER DEFAULT 0,
    current_version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

-- Module content table
CREATE TABLE IF NOT EXISTS module_contents (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES learning_modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(20) NOT NULL,
    content_format VARCHAR(20) DEFAULT 'markdown',
    content_body TEXT,
    content_url VARCHAR(500),
    order_index INTEGER DEFAULT 0,
    section VARCHAR(100),
    duration_seconds INTEGER,
    code_language VARCHAR(20),
    code_snippet TEXT,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module versions for content versioning
CREATE TABLE IF NOT EXISTS module_versions (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES learning_modules(id) ON DELETE CASCADE,
    version_number VARCHAR(20) NOT NULL,
    changelog TEXT,
    content_snapshot JSONB,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER
);

-- User progress tracking
CREATE TABLE IF NOT EXISTS user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES learning_modules(id) ON DELETE CASCADE,
    completion_percentage FLOAT DEFAULT 0.0,
    is_completed BOOLEAN DEFAULT FALSE,
    time_spent_minutes INTEGER DEFAULT 0,
    last_content_id INTEGER,
    last_position INTEGER DEFAULT 0,
    quiz_average_score FLOAT,
    exercises_completed INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module_id)
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES learning_modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    quiz_type VARCHAR(20) DEFAULT 'standard',
    time_limit_minutes INTEGER,
    passing_score FLOAT DEFAULT 70.0,
    max_attempts INTEGER DEFAULT 3,
    shuffle_questions BOOLEAN DEFAULT TRUE,
    show_answers BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    is_final_exam BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz questions
CREATE TABLE IF NOT EXISTS quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'multiple_choice',
    options JSONB DEFAULT '[]',
    correct_answer JSONB,
    code_template TEXT,
    expected_output TEXT,
    test_cases JSONB DEFAULT '[]',
    explanation TEXT,
    points INTEGER DEFAULT 1,
    difficulty VARCHAR(20) DEFAULT 'medium',
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User assessments (quiz attempts)
CREATE TABLE IF NOT EXISTS user_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    attempt_number INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'in_progress',
    score FLOAT,
    points_earned INTEGER DEFAULT 0,
    points_possible INTEGER DEFAULT 0,
    is_passed BOOLEAN,
    time_spent_seconds INTEGER,
    answers JSONB DEFAULT '{}',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Assessment results (individual question results)
CREATE TABLE IF NOT EXISTS assessment_results (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES user_assessments(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_answer JSONB,
    is_correct BOOLEAN,
    points_earned INTEGER DEFAULT 0,
    points_possible INTEGER DEFAULT 1,
    code_output TEXT,
    test_results JSONB DEFAULT '{}',
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_modules_slug ON learning_modules(slug);
CREATE INDEX IF NOT EXISTS idx_modules_difficulty ON learning_modules(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_modules_library ON learning_modules(library);
CREATE INDEX IF NOT EXISTS idx_modules_category ON learning_modules(category);
CREATE INDEX IF NOT EXISTS idx_contents_module ON module_contents(module_id);
CREATE INDEX IF NOT EXISTS idx_progress_user ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_module ON user_progress(module_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_module ON quizzes(module_id);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON quiz_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON user_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_quiz ON user_assessments(quiz_id);
CREATE INDEX IF NOT EXISTS idx_results_assessment ON assessment_results(assessment_id);
