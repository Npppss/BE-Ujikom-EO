CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    category event_category DEFAULT 'other',
    status event_status DEFAULT 'draft',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    is_online BOOLEAN DEFAULT FALSE,
    online_url VARCHAR(500),
    max_capacity INTEGER,
    current_registrations INTEGER DEFAULT 0,
    price FLOAT DEFAULT 0.0,
    currency VARCHAR(3) DEFAULT 'IDR',
    is_free BOOLEAN DEFAULT TRUE,
    flyer_url VARCHAR(500),
    banner_url VARCHAR(500),
    gallery_urls TEXT,
    organizer_id INTEGER NOT NULL REFERENCES users(id),
    organizer_name VARCHAR(255),
    organizer_email VARCHAR(255),
    organizer_phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    allow_waitlist BOOLEAN DEFAULT TRUE,
    require_approval BOOLEAN DEFAULT FALSE,
    check_in_started BOOLEAN DEFAULT FALSE,
    check_out_started BOOLEAN DEFAULT FALSE,
    check_in_qr_code VARCHAR(500) UNIQUE DEFAULT gen_random_uuid()::text,
    check_out_qr_code VARCHAR(500) UNIQUE DEFAULT gen_random_uuid()::text,
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Index untuk events
CREATE INDEX idx_events_organizer_id ON events(organizer_id);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_events_is_active ON events(is_active);