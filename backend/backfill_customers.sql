-- Copy the 171 students from crm_data.payload into the customers table.
-- Run AFTER supabase.sql + import_customers_171.sql + supabase_full.sql
-- Safe to re-run.

update crm_data set updated_at = now() where id = 1;

-- If the trigger did not fire (no payload change), force a no-op rewrite:
update crm_data
set payload = payload
where id = 1;

select count(*) as customers_rows from customers;
select jsonb_array_length(payload->'customers') as payload_customers from crm_data where id = 1;
