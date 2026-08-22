-- Camnemi CRM — full backend tables
-- Run AFTER backend/supabase.sql (crm_data + customers already exist)
-- Paste into Supabase → SQL Editor → Run

-- ===== Operational tables =====
create table if not exists agencies (
  name text primary key,
  commission text default '',
  policy text default '',
  note text default '',
  updated_at timestamptz not null default now()
);

create table if not exists fees (
  id uuid primary key default gen_random_uuid(),
  name text not null default '',
  amount text default '',
  policy text default '',
  sort int default 0,
  updated_at timestamptz not null default now()
);

create table if not exists partners (
  id uuid primary key default gen_random_uuid(),
  name text not null default '',
  note text default '',
  updated_at timestamptz not null default now()
);

create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  date text default '',
  type text default 'todo',
  title text default '',
  note text default '',
  updated_at timestamptz not null default now()
);

create table if not exists transactions (
  id uuid primary key default gen_random_uuid(),
  date text default '',
  type text default 'income',
  category text default '',
  amount numeric default 0,
  note text default '',
  updated_at timestamptz not null default now()
);

create table if not exists recs (
  id uuid primary key default gen_random_uuid(),
  col text default 'problems',
  title text default '',
  note text default '',
  updated_at timestamptz not null default now()
);

create table if not exists wiki_cats (
  id text primary key,
  icon text default '',
  title text default '',
  sort int default 0
);

create table if not exists wiki_notes (
  id text primary key,
  cat text default '',
  subj text default '',
  body text default '',
  replies jsonb default '[]'::jsonb,
  updated text default ''
);

create table if not exists wiki_docs (
  id text primary key,
  note_id text default '',
  cat text default '',
  name text default '',
  url text default '',
  meta jsonb default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists activity_log (
  id bigserial primary key,
  time text default '',
  user_name text default '',
  student text default '',
  action text default ''
);

create table if not exists app_settings (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- ===== University catalog =====
create table if not exists universities (
  id text primary key,
  name_kr text default '',
  name_en text default '',
  short_en text default '',
  loc text default '',
  type text default 'univ',
  logo text default '',
  students int,
  rank int,
  tuition jsonb default '{}'::jsonb,
  req jsonb default '{}'::jsonb,
  cert jsonb default '{}'::jsonb,
  majors_ba jsonb default '[]'::jsonb,
  majors_ma jsonb default '[]'::jsonb,
  extra jsonb default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists university_guides (
  univ_id text not null references universities(id) on delete cascade,
  track text not null,
  url text default '',
  primary key (univ_id, track)
);

create index if not exists universities_short_en_idx on universities (short_en);
create index if not exists universities_type_idx on universities (type);
create index if not exists wiki_notes_cat_idx on wiki_notes (cat);
create index if not exists tasks_date_idx on tasks (date);

-- ===== RLS (anon = same "Anyone" model as old Apps Script) =====
alter table agencies enable row level security;
alter table fees enable row level security;
alter table partners enable row level security;
alter table tasks enable row level security;
alter table transactions enable row level security;
alter table recs enable row level security;
alter table wiki_cats enable row level security;
alter table wiki_notes enable row level security;
alter table wiki_docs enable row level security;
alter table activity_log enable row level security;
alter table app_settings enable row level security;
alter table universities enable row level security;
alter table university_guides enable row level security;

do $$
declare t text;
begin
  foreach t in array array[
    'agencies','fees','partners','tasks','transactions','recs',
    'wiki_cats','wiki_notes','wiki_docs','activity_log','app_settings',
    'universities','university_guides'
  ]
  loop
    execute format('drop policy if exists %I on %I', t||'_anon_all', t);
    execute format(
      'create policy %I on %I for all to anon using (true) with check (true)',
      t||'_anon_all', t
    );
  end loop;
end $$;
