-- ============================================
-- Food Metrics Tables for The Life Hub
-- Run this in Supabase SQL Editor
-- ============================================

-- Daily food log (one row per day)
CREATE TABLE IF NOT EXISTS symphony_food_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    totals JSONB NOT NULL DEFAULT '{}'::jsonb,
    grade TEXT,
    grade_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Saved recipes / meal presets
CREATE TABLE IF NOT EXISTS symphony_food_recipes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_calories INTEGER DEFAULT 0,
    total_protein NUMERIC(6,1) DEFAULT 0,
    total_carbs NUMERIC(6,1) DEFAULT 0,
    total_fats NUMERIC(6,1) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security (open for anon for now, same as tasks table)
ALTER TABLE symphony_food_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE symphony_food_recipes ENABLE ROW LEVEL SECURITY;

-- Allow anon full access (matches existing symphony_tasks_master policy)
CREATE POLICY "Allow anon full access to food_log"
    ON symphony_food_log FOR ALL
    USING (true) WITH CHECK (true);

CREATE POLICY "Allow anon full access to food_recipes"
    ON symphony_food_recipes FOR ALL
    USING (true) WITH CHECK (true);

-- Index for fast date lookups on food log
CREATE INDEX IF NOT EXISTS idx_food_log_date ON symphony_food_log(date);
