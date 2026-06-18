-- Enable public UPSERT/UPDATE access for the master tasks table since we don't have Auth.
-- Drop any existing conflicting policy for UPDATE/INSERT if we need to.
DROP POLICY IF EXISTS "Allow public read-only access to master tasks." ON public.symphony_tasks_master;
DROP POLICY IF EXISTS "Allow public read access to master tasks." ON public.symphony_tasks_master;
DROP POLICY IF EXISTS "Allow public update access to master tasks." ON public.symphony_tasks_master;
DROP POLICY IF EXISTS "Allow public insert access to master tasks." ON public.symphony_tasks_master;

-- Recreate open policies for our drag-and-drop frontend (since it's protected by the hardcoded password)
CREATE POLICY "Allow public read access to master tasks."
ON public.symphony_tasks_master FOR SELECT USING (true);

CREATE POLICY "Allow public update access to master tasks."
ON public.symphony_tasks_master FOR UPDATE USING (true);

CREATE POLICY "Allow public insert access to master tasks."
ON public.symphony_tasks_master FOR INSERT WITH CHECK (true);

-- Fix the priority colors of the specific "Red" tasks we care about 
-- so they actually show up when the javascript filters for 'priority_color=eq.RED'
UPDATE public.symphony_tasks_master 
SET priority_color = 'RED'
WHERE title IN (
    'Morning Ride Drop-off',
    'Pick up dog (Quinn) poop from the lawn',
    'Walk Quinn (Zone 2 Cardio)',
    '15m train Quinn',
    'Shower & Prep'
);
