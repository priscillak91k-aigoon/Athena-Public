-- Supabase Migration: Finance Expenses/Bills Tracker
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)

CREATE TABLE IF NOT EXISTS symphony_expenses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    frequency TEXT NOT NULL DEFAULT 'weekly' CHECK (frequency IN ('weekly', 'fortnightly', 'monthly', 'yearly')),
    category TEXT NOT NULL DEFAULT 'essential' CHECK (category IN ('essential', 'flexible')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies (allow anon access, matching your existing pattern)
ALTER TABLE symphony_expenses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access to expenses" ON symphony_expenses FOR ALL USING (true) WITH CHECK (true);
