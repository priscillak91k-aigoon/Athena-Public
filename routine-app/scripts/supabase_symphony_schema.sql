-- Symphony Routine App - Database Schema Initializer
-- Paste and execute this entire snippet in your Supabase SQL Editor

-- 1. Create the Procurement Table
CREATE TABLE IF NOT EXISTS public.symphony_procurement (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category VARCHAR(10) NOT NULL CHECK (category IN ('NEED', 'WANT')),
    item TEXT NOT NULL,
    justification TEXT NOT NULL,
    athena_verdict VARCHAR(20) DEFAULT 'PENDING',
    athena_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create the Gamification Log Table
CREATE TABLE IF NOT EXISTS public.symphony_gamification_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date_logged DATE DEFAULT CURRENT_DATE,
    task_name TEXT NOT NULL,
    points_earned INTEGER NOT NULL CHECK (points_earned >= 1 AND points_earned <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Enable basic Row Level Security (RLS) policies
-- For this local dashboard, we allow anon reads, but only authenticated/service-role inserts.
-- If you want the bot to write, it will bypass RLS by using the Service Role key.
-- But the frontend JS needs to read using the Anon key.
ALTER TABLE public.symphony_procurement ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.symphony_gamification_log ENABLE ROW LEVEL SECURITY;

-- Allow Anon Read Access for Frontend
CREATE POLICY "Allow public read-only access to procurement." 
ON public.symphony_procurement FOR SELECT USING (true);

CREATE POLICY "Allow public read-only access to gamification logs." 
ON public.symphony_gamification_log FOR SELECT USING (true);

-- 4. Insert Initial Procurement Mock Data
INSERT INTO public.symphony_procurement (category, item, justification, athena_verdict, athena_comment) VALUES
('NEED', 'Water Flosser', 'Prevent plaque entering the bloodstream to protect my 9p21/ApoB risk. Essential daily maintenance.', 'APPROVED', 'Immediate biological ROI. Periodontal bacteria directly exacerbates systemic inflammation (CRP) and accelerates endothelial plaque formation. Purchase immediately.'),
('WANT', 'New Xbox Controller', 'Current one has minor stick drift. Purely recreational.', 'FLAGGED', 'Lowest priority capital allocation. Defer purchase until the end of the month if spare recreational budget remains.');
