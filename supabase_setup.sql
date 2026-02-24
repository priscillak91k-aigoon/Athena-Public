-- Supabase initialization script for Athena Life Engine
-- Paste this into the Supabase SQL Editor and hit Run

CREATE TABLE IF NOT EXISTS user_data (
    id integer PRIMARY KEY DEFAULT 1,
    schedule_payload text,
    history_payload text,
    memory_payload text,
    excel_payload text,
    dashboard_points integer DEFAULT 0
);

-- Insert the initial blank row
INSERT INTO user_data (id, schedule_payload, history_payload, memory_payload, excel_payload, dashboard_points)
VALUES (1, '', '', '', '', 0)
ON CONFLICT (id) DO NOTHING;

-- Enable RLS and allow the Anon key to read/write this specific table
-- (Since the app runs locally on your phone and the bot uses the anon key)
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select" ON user_data FOR SELECT USING (true);
CREATE POLICY "Allow public update" ON user_data FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON user_data FOR INSERT WITH CHECK (true);
