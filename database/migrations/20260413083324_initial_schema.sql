-- Initial schema for SJK SmartView

-- Пользователи (Сотрудники Shojiki)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'manager',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Локации (Адреса экранов)
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT, -- 'Outdoor LED', '3D LED', 'Billboard', 'Indoor LCD'
    description TEXT,
    address TEXT,
    coords_lat FLOAT,
    coords_lng FLOAT,
    primary_photo_url TEXT,
    screen_geometry JSONB, -- { "corners": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] }
    aspect_ratio FLOAT DEFAULT 1.77,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Мокапы (История генераций)
CREATE TABLE IF NOT EXISTS mockups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
    creative_url TEXT NOT NULL,
    result_url TEXT,
    metadata JSONB, -- AI confidence, processing time, etc.
    status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Триггеры для updated_at (опционально, но полезно)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
