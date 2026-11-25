-- Run this in the Supabase SQL Editor.
create table if not exists public.books (
  upc                text primary key,          -- natural unique key; makes upserts idempotent
  title              text not null,
  category           text,
  price_gbp          numeric(8,2) not null,
  price_incl_tax_gbp numeric(8,2),
  tax_gbp            numeric(8,2),
  in_stock           boolean not null default false,
  stock_count        integer not null default 0,
  rating             smallint check (rating between 1 and 5),
  num_reviews        integer not null default 0,
  description        text,
  image_url          text,
  product_url        text not null,
  scraped_at         timestamptz not null default now()
);

create index if not exists books_category_idx on public.books (category);

-- Server-side script uses the service_role key (bypasses RLS). Enable RLS so the
-- public anon key cannot write; allow public read-only access.
alter table public.books enable row level security;
create policy "public read" on public.books for select using (true);
