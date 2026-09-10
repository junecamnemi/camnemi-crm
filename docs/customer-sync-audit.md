# Customer persistence audit

## Scope and evidence

- User symptoms: pipeline/list cards reappear after deletion; status changes fail to persist.
- Inspected public GitHub Pages HTML and local tracked `index.html`; text is identical (line-ending bytes differ).
- Production database inspection was read-only. No live customer rows were created, updated, or deleted.
- Observed customer rows: 176; distinct normalized names: 176; duplicate-name groups: 0.
- `customers` has primary key `id`, no user triggers, and no inbound foreign keys at time of inspection.
- Real tests use synthetic data and intercepted HTTP, not production customers.

## Reproduced root cause

`syncPush()` declares `remoteCust` inside the nested merge `try`, then references it outside that lexical scope in its stale-seed filter. Running the actual original function with a synthetic customer returns false, performs zero writes, and logs:

```
Backend push failed ReferenceError: remoteCust is not defined
```

This invalidates previous assumptions that all stage reverts are due to duplicate names.

## Other source-level failure paths

1. `deleteCustomer()` removes the DOM card but does not issue a server DELETE or record a deletion operation. Whole-snapshot upserts cannot represent deletion.
2. `syncPush()` merges server rows absent from the DOM back into its payload; `syncPull()` appends every local-only row, even previously server-backed rows removed elsewhere.
3. Cloud boot pushes local cache before pulling authoritative state. `seedKoreaStudents()` also runs whenever Korea has zero cards, including after a cloud restore.
4. `forcePushNow()` and unload manually clear the sync lock; unload sends POST upserts from timestamps. This can overlap writes and recreate absent records.
5. `saveNow()` gates on the legacy Apps Script URL instead of Supabase configuration. Debounced saves can be dropped while syncing.
6. `archiveCustomer()` and `batchMove()` rely on render-side autosave instead of explicit user-mutation persistence.
7. `autoPullAgencySubmissions()` and manual submission import compare only names in the New pipeline. Moving a student to Korea or deleting a student makes their historic submission eligible again.
8. Customer saves originally delete/recreate whole ancillary tables (fees, partners, tasks, transactions, recommendations). These separate requests are non-atomic and risk lost writes in concurrent clients.

## Backend risk: not fixed by hiding UI

Production RLS is enabled, but `customers_anon_write` allows ALL operations to `anon` with both predicates true. Anonymous SELECT and similarly permissive policies exist on `app_settings`, `tasks`, and `transactions`. A client-side Google-domain check is not database authorization.

Do not put the service-role key in this static app. Proper remediation requires authenticated Supabase JWTs / a server-verified identity bridge and least-privilege RLS. Plan and test the login and agency-submission flow before applying restrictive policies, to avoid locking out legitimate users. No auth-policy migration was applied in this task.

## Deployment requirements / remaining boundaries

- Frontend fixes cannot stop already-open OLD clients with permissive API access from posting stale full-row upserts. On rollout, refresh every client; durable server-side delete tombstones and row-version enforcement are the stronger follow-up.
- Automatic historical agency-submission replay is disabled in the customer fix; new submissions require the existing manual import action. This is a deliberate behavior change to stop boot-time resurrection, not a claim that a server-side consumed-submission ledger exists. Manual import from another browser without a local tombstone may reimport a deleted submission; server-side tracking is still required.
- The outbox survives refresh of its tab using a sessionStorage writer ID and localStorage operations. Closing that tab without restoring its session does not automatically adopt the old writer's queued operations; browser storage clearing removes unsent state. A recovery UI/lease protocol is follow-up work.
- Ambiguous new-customer insert results are retained for review instead of blindly POSTing again (which could recreate a deleted row). This may require operator reconciliation after connection loss. Existing-customer PATCH and DELETE are safely retryable, and failures must not block unrelated IDs.
- Do not repair data by deleting same-name records automatically: different people may share a name.
- Test old-client stale inserts, duplicate-ID create retry, concurrent status edits, independent-field edits, pending delete during reload, and server errors before a database concurrency migration.
- The current read limit of 2,000 customers is not a complete pagination strategy; do not infer deletion from a partial result. Add paging before the dataset reaches that limit.
- No production deployment, DB cleanup, or credential/policy change is authorized by this audit alone.

## Broader frontend/backend review (separate follow-up work)

The following are not claimed fixed by the customer sync patch:

- `handleGoogleCredential` decodes a JWT client-side; `initAuth` trusts a cached email. The public `?agency=` route enters shared CRM boot and whole-table read paths. Separate external submission UI from internal read access.
- `backend/Code.gs` file/backup handlers accept caller-supplied folder IDs; source sets `ANYONE_WITH_LINK` for uploads/backups. Actual deployed Apps Script access and Drive sharing were NOT checked. Audit ownership, add authentication and folder scope enforcement before changing these APIs.
- `renderList` interpolates custom column names from shared app settings into HTML/attributes/inline handlers. Validate settings schema and replace untrusted HTML composition with text nodes/event listeners.
- Agencies/wiki entity deletions remove local values but upsert-only persistence cannot delete missing server entities. Explicit ID deletes and relationship policies are needed; do not infer removal of actual Drive files.
- Ancillary tables still use delete/reinsert when THEY are edited. Change-detection on customer saves reduces exposure but does not make those writes transactional or safe under concurrent edits.
- List filter handling and column-order application differ between header/body and kanban. Hidden-customer regression is in scope; general sorting/filter redesign is not.
- `saveWikiNote` uses block-scoped `n` outside its block in logging, causing an exception after saving.
- `refreshKoreaDocs`/`fuzzyFindFolderId` use name-based folder matching; ambiguous names can resolve to the wrong folder and empty successful listings may leave stale cache.
- Historical SQL files can recreate the removed full-table mirror trigger or permissive anon policies. Do not re-run legacy bootstrap SQL as a migration.

## Verification commands

```bash
node --test tests/customer-sync.test.cjs
node tests/crm-ui-sync.spec.cjs --baseline
node tests/crm-ui-sync.spec.cjs
```

The browser harness accepts `PLAYWRIGHT_MODULE` and `CHROME_PATH` overrides. Its default isolated test dependency is `C:/Users/USER/AppData/Local/Temp/crm-sync-test/node_modules/playwright`. It reads the HTML once, prints its SHA256, serves it locally with synthetic backend defaults, blocks nonlocal traffic, and uses only a fake in-memory DB.

Baseline (`git HEAD:index.html`, text matches fetched production): independently reproduced **0/8 browser scenarios passing, 19 failed checks**, including the `remoteCust` error. Failure is the expected baseline result, not a harness-success claim. Final independently executed result: **19/19 Node regression tests pass; 8/8 real-browser scenarios pass, 0 failed checks**. `node --check` on the main inline script and `git diff --check` pass. The browser-tested final source SHA256 (Node UTF-8 bytes) is `6ccca89789811a958f7d2738fadca0db69c6c0152d52d4af477dbdeac459700a`, rechecked against the final file. This verifies the isolated synthetic scenarios, not a live production rollout.

Node tests cover failed-write/reload deletion, partial-field updates preserving remote fields, serial saves, explicit insert vs stale cache, authoritative empty reads, no cloud seeding/unload writes, archive/batch moves, pending insert, lost insert acknowledgement, and insert-in-flight edits. UI tests cover actual modal Save/Delete/Archive, list visibility, reload, a preloaded second tab, hide, batch archive, and agency reimport prevention.
