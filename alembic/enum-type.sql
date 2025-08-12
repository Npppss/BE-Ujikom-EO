-- Membuat enum untuk status event
CREATE TYPE event_status AS ENUM ('draft', 'published', 'ongoing', 'completed', 'cancelled');

-- Membuat enum untuk kategori event
CREATE TYPE event_category AS ENUM ('business', 'entertainment', 'education', 'technology', 'health', 'sports', 'culture', 'other');