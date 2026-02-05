-- Supabase SQL Schema for Assignment Platform
-- Run this in your Supabase SQL Editor

-- ============ Users Table ============
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============ Assignments Table ============
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    max_marks INTEGER DEFAULT 100,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============ Submissions Table ============
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed')),
    
    -- Unique constraint: one submission per student per assignment
    UNIQUE(assignment_id, student_id)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

-- ============ Reviews Table ============
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    marks INTEGER NOT NULL CHECK (marks >= 0),
    feedback TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- One review per submission
    UNIQUE(submission_id)
);

-- Index for faster submission lookups
CREATE INDEX IF NOT EXISTS idx_reviews_submission ON reviews(submission_id);

-- ============ Row Level Security (Optional) ============
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Policies (adjust based on your security needs)
-- For now, allow service role full access
CREATE POLICY "Service role has full access to users"
    ON users FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to assignments"
    ON assignments FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to submissions"
    ON submissions FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to reviews"
    ON reviews FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============ Sample Data (Optional) ============
-- Uncomment to insert sample admin user (password: admin123)
-- INSERT INTO users (email, password_hash, name, role) 
-- VALUES ('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.oVYHeYYqKIhY5m', 'Admin User', 'admin');
