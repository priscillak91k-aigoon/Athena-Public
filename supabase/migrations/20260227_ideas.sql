-- Supabase Migration: Ideas (Brain Dump + Bucket List) Persistence
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)

CREATE TABLE IF NOT EXISTS symphony_ideas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    list_type TEXT NOT NULL CHECK (list_type IN ('bucket', 'braindump')),
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies (allow anon access, matching your existing pattern)
ALTER TABLE symphony_ideas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access to ideas" ON symphony_ideas FOR ALL USING (true) WITH CHECK (true);
