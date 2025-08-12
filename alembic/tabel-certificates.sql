CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    certificate_id VARCHAR(20) UNIQUE DEFAULT upper(substring(gen_random_uuid()::text from 1 for 8)),
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES certificate_templates(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    certificate_type VARCHAR(50) DEFAULT 'participation',
    template_url VARCHAR(500),
    generated_url VARCHAR(500),
    file_format VARCHAR(10) DEFAULT 'pdf',
    participant_name VARCHAR(255) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_date TIMESTAMP NOT NULL,
    event_location VARCHAR(255),
    achievement_score FLOAT,
    achievement_level VARCHAR(50),
    completion_hours FLOAT,
    is_issued BOOLEAN DEFAULT FALSE,
    issued_date TIMESTAMP,
    issued_by VARCHAR(255),
    is_valid BOOLEAN DEFAULT TRUE,
    expiry_date TIMESTAMP,
    verification_code VARCHAR(100) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Index untuk certificates
CREATE INDEX idx_certificates_certificate_id ON certificates(certificate_id);
CREATE INDEX idx_certificates_event_id ON certificates(event_id);
CREATE INDEX idx_certificates_user_id ON certificates(user_id);
CREATE INDEX idx_certificates_verification_code ON certificates(verification_code);