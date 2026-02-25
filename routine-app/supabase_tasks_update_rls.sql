-- Enable Anonymous UPDATE access for the Tasks Master table
-- This allows the frontend website to change task colors in real-time.

CREATE POLICY "Allow public update access to master tasks."
ON public.symphony_tasks_master FOR UPDATE USING (true);
