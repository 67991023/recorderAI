-- Create database schema
CREATE TABLE IF NOT EXISTS recordings (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_recordings_created_at ON recordings(created_at DESC);
CREATE INDEX idx_recordings_word_count ON recordings(word_count);

-- Insert sample data
INSERT INTO recordings (text, word_count, character_count) VALUES
('สวัสดีครับ ทดสอบระบบบันทึกเสียง', 4, 30),
('การวิเคราะห์ข้อมูลด้วย Machine Learning', 5, 42),
('โปรเจคนี้ใช้ Docker Compose สำหรับการ Deploy', 7, 51);

-- Create a view for statistics
CREATE OR REPLACE VIEW recording_statistics AS
SELECT 
    COUNT(*) as total_recordings,
    AVG(word_count)::INTEGER as avg_word_count,
    MAX(word_count) as max_word_count,
    MIN(word_count) as min_word_count,
    SUM(word_count) as total_words
FROM recordings;