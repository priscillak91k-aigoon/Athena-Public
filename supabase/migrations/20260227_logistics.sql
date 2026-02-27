-- Supabase Migration: Open Logistics Feature
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)

-- 1. Logistics items table
CREATE TABLE IF NOT EXISTS symphony_logistics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'done')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Logistics sub-tasks table
CREATE TABLE IF NOT EXISTS symphony_logistics_subtasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    logistics_id UUID REFERENCES symphony_logistics(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. RLS Policies (allow anon access, matching your existing pattern)
ALTER TABLE symphony_logistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE symphony_logistics_subtasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access to logistics" ON symphony_logistics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to logistics subtasks" ON symphony_logistics_subtasks FOR ALL USING (true) WITH CHECK (true);
