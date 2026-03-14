-- Workshop Supabase Schema
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query → Paste → Run)

-- ─── WISHLISTS ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.workshop_wishlists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    price TEXT,
    link TEXT,
    why TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.workshop_wishlists ENABLE ROW LEVEL SECURITY;

CREATE POLICY "workshop_wishlists_public_read"
    ON public.workshop_wishlists FOR SELECT USING (true);

CREATE POLICY "workshop_wishlists_anon_insert"
    ON public.workshop_wishlists FOR INSERT WITH CHECK (true);

CREATE POLICY "workshop_wishlists_anon_delete"
    ON public.workshop_wishlists FOR DELETE USING (true);


-- ─── IDEAS ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.workshop_ideas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    text TEXT NOT NULL,
    category TEXT DEFAULT 'general'
        CHECK (category IN ('general', 'project', 'business', 'make', 'try')),
    added_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.workshop_ideas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "workshop_ideas_public_read"
    ON public.workshop_ideas FOR SELECT USING (true);

CREATE POLICY "workshop_ideas_anon_insert"
    ON public.workshop_ideas FOR INSERT WITH CHECK (true);

CREATE POLICY "workshop_ideas_anon_delete"
    ON public.workshop_ideas FOR DELETE USING (true);


-- ─── LISTS ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.workshop_lists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    list_name TEXT NOT NULL,
    icon TEXT DEFAULT '📝',
    items JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.workshop_lists ENABLE ROW LEVEL SECURITY;

CREATE POLICY "workshop_lists_public_read"
    ON public.workshop_lists FOR SELECT USING (true);

CREATE POLICY "workshop_lists_anon_insert"
    ON public.workshop_lists FOR INSERT WITH CHECK (true);

CREATE POLICY "workshop_lists_anon_update"
    ON public.workshop_lists FOR UPDATE USING (true);

CREATE POLICY "workshop_lists_anon_delete"
    ON public.workshop_lists FOR DELETE USING (true);
