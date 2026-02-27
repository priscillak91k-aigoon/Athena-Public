-- Run this in your Supabase SQL Editor to create the Supplement Inventory table.

create table public.symphony_supp_inventory (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  total_capacity integer not null default 0,
  current_stock integer not null default 0,
  daily_dose integer not null default 1,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table public.symphony_supp_inventory enable row level security;

-- Create policies for public access (similar to the food logs)
create policy "Allow public insert" on public.symphony_supp_inventory for insert with check (true);
create policy "Allow public select" on public.symphony_supp_inventory for select using (true);
create policy "Allow public update" on public.symphony_supp_inventory for update using (true);
create policy "Allow public delete" on public.symphony_supp_inventory for delete using (true);
