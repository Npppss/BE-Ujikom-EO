CREATE TABLE certificate_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    template_type VARCHAR(50) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    design_config TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Index untuk certificate_templates
CREATE INDEX idx_certificate_templates_is_active ON certificate_templates(is_active);