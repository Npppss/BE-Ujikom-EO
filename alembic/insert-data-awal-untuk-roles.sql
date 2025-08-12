-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Administrator with full access', '["all"]'),
('organizer', 'Event organizer with event management permissions', '["event_management", "attendance_management", "certificate_management"]'),
('participant', 'Event participant with basic access', '["event_registration", "attendance_check"]');