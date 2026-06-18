-- Symphony Routine App - Dynamic Tasks Schema Initializer
-- Paste and execute this snippet in your Supabase SQL Editor

-- 1. Create the Master Tasks Table
CREATE TABLE IF NOT EXISTS public.symphony_tasks_master (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    time_target TEXT, -- e.g. '08:50 AM' or 'Daily Flexible'
    priority_color VARCHAR(10) NOT NULL CHECK (priority_color IN ('RED', 'ORANGE', 'GREEN')),
    points INTEGER DEFAULT 1,
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Enable RLS for Frontend Fetching
ALTER TABLE public.symphony_tasks_master ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read-only access to master tasks." 
ON public.symphony_tasks_master FOR SELECT USING (true);

-- 3. Insert Initial Categorized Data (from the Traffic Light System)
INSERT INTO public.symphony_tasks_master (title, description, time_target, priority_color, points, tags) VALUES
-- RED: Critical / Time-Locked
('Morning Ride Drop-off', 'Sarah and the boys (School/Kindy)', '08:50 AM', 'RED', 2, ARRAY['Family']),
('Parker Pick Up', 'Leave with Tash at 2:45 PM for 3:00 PM pickup', '02:45 PM', 'RED', 2, ARRAY['Family']),

-- ORANGE: Daily Mandates / Flexible Timing
('Morning Supplements', 'K2, L-Theanine, NAC', 'Daily Flexible', 'ORANGE', 1, ARRAY['Health', 'Bio']),
('Quinny''s Walk (Zone 2 Cardio)', '1-Hr brisk walk + 10 mins training', 'Daily Flexible', 'ORANGE', 5, ARRAY['Pet Care', 'Health']),
('Pick up Quinn''s Poop', 'Clear the lawn', 'Daily Flexible', 'ORANGE', 1, ARRAY['Pet Care', 'Chores']),
('Core Rest Phase (Nap)', 'Crucial recovery and energy before afternoon rush', 'Daily Flexible', 'ORANGE', 2, ARRAY['Rest']),
('Post-Drop-off Reset', 'Dishes, put stuff away, make boys bed', 'Daily Flexible', 'ORANGE', 3, ARRAY['Cleaning']),
('Lux (Vacuum) Ground Floor', 'General vacuuming', 'Daily Flexible', 'ORANGE', 2, ARRAY['Cleaning']),
('Empty inside bins', 'Empty and refill liners', 'Daily Flexible', 'ORANGE', 1, ARRAY['Cleaning']),
('Bring in outside bins', 'Evening sweep', 'Daily Flexible', 'ORANGE', 1, ARRAY['Chores']),
('Air house out & Spray couches', 'Make the house smell nice', 'Daily Flexible', 'ORANGE', 1, ARRAY['Cleaning']),
('Kids Toys Upright', 'Make sure outside kids toys are left upright', 'Daily Flexible', 'ORANGE', 1, ARRAY['Mental Load']),
('Discard used tooth floss', 'Mental load cleanup', 'Daily Flexible', 'ORANGE', 1, ARRAY['Mental Load']),

-- GREEN: Moveable / Weekly / Periodic
('Quinny''s Furminator Brush', 'Deep groom taking ~1 hour', 'Weekly', 'GREEN', 4, ARRAY['Pet Care']),
('3-Day Longevity Workout Split', 'Full Session', 'Weekly (3x)', 'GREEN', 5, ARRAY['Health', 'Workout']),
('Catch up on washing', 'Hang outside if decent weather', 'Moveable', 'GREEN', 3, ARRAY['Chores']),
('Sort & fold washing', 'Pop aside for others', 'Moveable', 'GREEN', 2, ARRAY['Chores']),
('Clean my shoes', 'Periodic maintenance', 'Moveable', 'GREEN', 1, ARRAY['Chores']),
('Clean the vacuum (Lux) head', 'Weekly maintenance', 'Weekly', 'GREEN', 2, ARRAY['Maintenance']),
('Clean Sarah''s car', 'Due to Quinny''s fur', 'Weekly', 'GREEN', 4, ARRAY['Maintenance']),
('Clean the toilet and bathroom', 'Weekly deep clean', 'Weekly', 'GREEN', 4, ARRAY['Cleaning']),
('Caravan Track Vehicle Logistics', 'Weekly check', 'Weekly', 'GREEN', 3, ARRAY['Logistics']),
('Clean clothes drier and washer', 'Monthly maintenance', 'Monthly', 'GREEN', 4, ARRAY['Maintenance']),
('Message sister (Tresha)', 'Monthly check-in', 'Monthly', 'GREEN', 2, ARRAY['Family']),
('Message mum (Rachel)', 'Monthly check-in', 'Monthly', 'GREEN', 2, ARRAY['Family']),
('Message foster mum (Jacinta)', 'Monthly check-in', 'Monthly', 'GREEN', 2, ARRAY['Family']),
('Message foster sister (Shakira)', 'Monthly check-in', 'Monthly', 'GREEN', 2, ARRAY['Family']);
