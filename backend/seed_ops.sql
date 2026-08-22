-- Seed default ops data. Run AFTER supabase_full.sql.
-- Safe to re-run (on conflict do nothing / ignore).

insert into agencies (name, commission, policy, note) values
  ('CAMNEMI', '—', 'In-house / direct (no external agency). Default.', ''),
  ('COSTA', '10%', 'Partner agency. Payment on admission confirmation.', ''),
  ('Khema', '12%', 'Partner agency. Quarterly performance review.', ''),
  ('Kimsous', '—', 'Partner agency.', ''),
  ('Sen Chao', '—', 'Partner agency.', ''),
  ('JK', '—', 'Partner agency.', ''),
  ('Din Lina', '—', 'Partner agency.', '')
on conflict (name) do nothing;

insert into fees (name, amount, policy, sort)
select * from (values
  ('Application Service Fee', 'USD 500', 'Charged per application. Non-refundable after submission.', 1),
  ('Admission Handling Fee', 'USD 300', 'Document review and admission coordination.', 2),
  ('VISA Processing Fee', 'USD 200', 'Embassy/consulate coordination and document prep.', 3),
  ('Admin / Service Charge', 'USD 150', 'General administration and support.', 4)
) as v(name, amount, policy, sort)
where not exists (select 1 from fees f where f.name = v.name);

insert into wiki_cats (id, icon, title, sort) values
  ('docs', '📄', 'Documents', 1),
  ('notice', '🏫', 'Special Notice of School', 2),
  ('visa', '🛂', 'VISA Application', 3)
on conflict (id) do nothing;

insert into wiki_notes (id, cat, subj, body, replies, updated) values
  ('w1', 'docs', 'Required documents to apply to school',
   E'1. Application form\n2. Passport copy\n3. High school diploma + transcript\n4. Bank statement (proof of funds)\n5. Study plan / letter of intent\n6. Recommendation letter\n7. Passport photos (3x4)\n8. Family book / birth certificate',
   '[]'::jsonb, '2026-01-01 09:00'),
  ('w2', 'visa', 'Required documents to apply for D-4 / D-2 visa',
   E'1. Visa application form\n2. Valid passport\n3. Certificate of Admission from school\n4. Bank balance certificate (KRW ~10M)\n5. Passport photos (3x4, white bg)\n6. Proof of accommodation\n7. Invitation letter\n8. Health checkup certificate (if required)',
   '[]'::jsonb, '2026-01-01 09:00'),
  ('w3', 'notice', 'How to submit documents to the school office',
   'Submit the completed application package to the international office at least 2 weeks before the deadline. Bring the original documents for verification.',
   '[]'::jsonb, '2026-01-01 09:00')
on conflict (id) do nothing;

insert into app_settings (key, value) values
  ('list_view', '{"listCustomCols":[],"hiddenListCols":[],"listColOrder":[]}'::jsonb)
on conflict (key) do nothing;
