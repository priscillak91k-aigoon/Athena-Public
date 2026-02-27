-- Supabase Migration: Calendar Events
-- Weekly/Monthly Planning System

CREATE TABLE IF NOT EXISTS symphony_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    event_date DATE NOT NULL,
    recurrence TEXT DEFAULT 'once' CHECK (recurrence IN ('once', 'weekly', 'monthly', 'yearly')),
    color TEXT DEFAULT 'BLUE' CHECK (color IN ('RED', 'ORANGE', 'GREEN', 'BLUE', 'PURPLE')),
    category TEXT DEFAULT 'other',
    time_of_day TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE symphony_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access to events" ON symphony_events FOR ALL USING (true) WITH CHECK (true);
