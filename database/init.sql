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
('โปรเจคนี้ใช้ Docker Compose สำหรับการ Deploy', 7, 51),
('K-Means clustering เป็น unsupervised learning algorithm', 6, 55),
('ภาษาไทย Thai NLP tokenization', 4, 31),
('การประมวลผลเสียงด้วย Speech-to-Text หรือ STT', 6, 46),
('Python Flask API backend REST endpoints', 5, 40),
('PostgreSQL database query optimization index', 5, 45),
('Docker container deployment production environment nginx', 5, 57),
('Silhouette score validation cluster quality measurement metric', 7, 63),
('สวัสดี', 1, 7),
('Chart.js visualization scatter plot cluster colors frontend dashboard', 8, 71);

-- Create a view for statistics
CREATE OR REPLACE VIEW recording_statistics AS
SELECT 
    COUNT(*) as total_recordings,
    AVG(word_count)::INTEGER as avg_word_count,
    MAX(word_count) as max_word_count,
    MIN(word_count) as min_word_count,
    SUM(word_count) as total_words
FROM recordings;