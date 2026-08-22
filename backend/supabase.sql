-- Camnemi CRM — Supabase / Postgres
-- Paste this into: https://supabase.com/dashboard → SQL Editor → New query → Run
-- Then Project Settings → API: copy Project URL + anon public key into the CRM Data tools.

create table if not exists crm_data (
  id int primary key default 1 check (id = 1),
  payload jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

insert into crm_data (id, payload)
values (1, '{"version":1,"customers":[],"agencies":[],"partners":[],"tasks":[],"transactions":[],"recs":[]}'::jsonb)
on conflict (id) do nothing;

create table if not exists customers (
  id text primary key,
  pipe text default 'new',
  stage text default 'contact',
  name text not null default '',
  age text default '',
  agency text default '',
  program text default '',
  school text default '',
  appdate text default '',
  contact text default '',
  email text default '',
  loan text default '',
  topik text default '',
  ielts text default '',
  notes jsonb default '[]'::jsonb,
  birthdate text default '',
  noqr text default '',
  illegal text default '',
  denied text default '',
  loan_flag text default '',
  payments jsonb default '[]'::jsonb,
  recent text default '',
  folder_id text default '',
  folder_url text default '',
  hidden text default '',
  siemreap text default '',
  custom_fields jsonb default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create index if not exists customers_pipe_stage_idx on customers (pipe, stage);
create index if not exists customers_name_idx on customers (upper(name));

-- Mirror crm_data.payload.customers into the customers table after each save
create or replace function crm_sync_customers_from_payload()
returns trigger language plpgsql as $$
begin
  delete from customers;
  insert into customers (
    id, pipe, stage, name, age, agency, program, school, appdate,
    contact, email, loan, topik, ielts, notes, birthdate,
    noqr, illegal, denied, loan_flag, payments, recent,
    folder_id, folder_url, hidden, siemreap, custom_fields
  )
  select
    coalesce(c->>'id', 'c' || substr(md5(random()::text),1,8)),
    coalesce(c->>'pipe','new'),
    coalesce(c->>'stage','contact'),
    coalesce(c->>'name',''),
    coalesce(c->>'age',''),
    coalesce(c->>'agency',''),
    coalesce(c->>'program',''),
    coalesce(c->>'school',''),
    coalesce(c->>'appdate',''),
    coalesce(c->>'contact',''),
    coalesce(c->>'email',''),
    coalesce(c->>'loan',''),
    coalesce(c->>'topik',''),
    coalesce(c->>'ielts',''),
    coalesce(c->'notes','[]'::jsonb),
    coalesce(c->>'birthdate',''),
    coalesce(c->>'noqr',''),
    coalesce(c->>'illegal',''),
    coalesce(c->>'denied',''),
    coalesce(c->>'loanFlag', c->>'loan_flag', ''),
    case
      when jsonb_typeof(c->'payments') = 'array' then c->'payments'
      when c->>'payments' is null or c->>'payments' = '' then '[]'::jsonb
      else coalesce(c->'payments','[]'::jsonb)
    end,
    coalesce(c->>'recent',''),
    coalesce(c->>'folderId', c->>'folder_id', ''),
    coalesce(c->>'folderUrl', c->>'folder_url', ''),
    coalesce(c->>'hidden',''),
    coalesce(c->>'siemreap',''),
    coalesce(c->'customFields','{}'::jsonb)
  from jsonb_array_elements(coalesce(new.payload->'customers','[]'::jsonb)) as c
  on conflict (id) do update set
    pipe = excluded.pipe, stage = excluded.stage, name = excluded.name,
    age = excluded.age, agency = excluded.agency, program = excluded.program,
    school = excluded.school, appdate = excluded.appdate, contact = excluded.contact,
    email = excluded.email, loan = excluded.loan, topik = excluded.topik,
    ielts = excluded.ielts, notes = excluded.notes, birthdate = excluded.birthdate,
    noqr = excluded.noqr, illegal = excluded.illegal, denied = excluded.denied,
    loan_flag = excluded.loan_flag, payments = excluded.payments, recent = excluded.recent,
    folder_id = excluded.folder_id, folder_url = excluded.folder_url,
    hidden = excluded.hidden, siemreap = excluded.siemreap,
    custom_fields = excluded.custom_fields, updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_crm_sync_customers on crm_data;
create trigger trg_crm_sync_customers
after insert or update of payload on crm_data
for each row execute function crm_sync_customers_from_payload();

alter table crm_data enable row level security;
alter table customers enable row level security;

-- Open to the anon key so the static GitHub Pages app can read/write
-- (same model as the old Apps Script "Anyone" web app).
-- After you turn on Supabase Auth (Google, @camnemi.com only), replace
-- these with: using (auth.role() = 'authenticated')
drop policy if exists crm_data_anon_all on crm_data;
create policy crm_data_anon_all on crm_data for all to anon using (true) with check (true);

drop policy if exists customers_anon_read on customers;
create policy customers_anon_read on customers for select to anon using (true);

-- Table Editor (you, logged into dashboard) can still edit via the service role.
