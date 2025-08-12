CREATE TABLE certificate_verifications (
    id SERIAL PRIMARY KEY,
    certificate_id INTEGER NOT NULL REFERENCES certificates(id) ON DELETE CASCADE,
    verification_code VARCHAR(100) NOT NULL,
    verification_date TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_valid BOOLEAN DEFAULT TRUE,
    verification_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk certificate_verifications
CREATE INDEX idx_certificate_verifications_certificate_id ON certificate_verifications(certificate_id);
CREATE INDEX idx_certificate_verifications_verification_code ON certificate_verifications(verification_code);