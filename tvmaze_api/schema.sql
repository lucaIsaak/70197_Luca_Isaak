-- Run this in the Supabase SQL Editor.
create table if not exists public.shows (
  id             integer primary key,           -- TVmaze show id; makes upserts idempotent
  name           text not null,
  type           text,
  language       text,
  genres         text[] not null default '{}',
  status         text,
  premiered      date,
  ended          date,
  runtime        integer,
  rating         numeric(3,1),
  network        text,
  country        text,
  official_site  text,
  summary        text,
  image_url      text,
  tvmaze_url     text not null,
  fetched_at     timestamptz not null default now()
);

create index if not exists shows_rating_idx on public.shows (rating desc);

-- Server-side script uses the service_role key (bypasses RLS). Enable RLS so the
-- public anon key cannot write; allow public read-only access.
alter table public.shows enable row level security;
create policy "public read" on public.shows for select using (true);
