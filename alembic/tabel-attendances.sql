CREATE TABLE attendances (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    check_in_time TIMESTAMP WITH TIME ZONE,
    check_out_time TIMESTAMP WITH TIME ZONE,
    check_in_qr_scanned BOOLEAN DEFAULT FALSE,
    check_out_qr_scanned BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Index untuk attendances
CREATE INDEX idx_attendances_event_id ON attendances(event_id);
CREATE INDEX idx_attendances_user_id ON attendances(user_id);