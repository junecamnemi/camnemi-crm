# Isolated CRM browser regressions

Run from the repository root:

```bash
node tests/crm-ui-sync.spec.cjs --baseline
node tests/crm-ui-sync.spec.cjs
```

`--baseline` reads `git show HEAD:index.html`; current reads `index.html`. Before the fix is committed, HEAD is the failing baseline. After commit, HEAD includes the fix: to reproduce the original failure, save the pre-fix commit's HTML and use `--source=...` instead. Each run captures the full source once before launching, prints SHA256, and serves that immutable in-memory snapshot through an ephemeral Node HTTP server on `127.0.0.1`. `--source=C:/path/index.html` selects a saved source instead.

The standalone script uses Playwright (not `@playwright/test`) from the existing temporary install, or `PLAYWRIGHT_MODULE`, or a normal `playwright` install. `CHROME_PATH` can override the auto-detected local Chrome/Edge executable. It uses a disposable headless browser context, not a user's profile.

Optional structured evidence:

```bash
CRM_UI_REPORT=tests/fixtures/crm-ui-sync/baseline-result.json node tests/crm-ui-sync.spec.cjs --baseline
CRM_UI_REPORT=tests/fixtures/crm-ui-sync/current-result.json node tests/crm-ui-sync.spec.cjs
```

## Fixture differences / network safety

- All customer rows are generated synthetic ALPHA/BETA/GAMMA/DELTA records inside the test; no production data or secrets are read.
- The served HTML strips preconnect/DNS-prefetch hints and rewrites embedded Supabase defaults to the ephemeral local server + a noncredential fake key. The on-disk application is never edited.
- Local storage is initially seeded with synthetic data and synthetic local auth. The application's existing localhost auth bypass and real `bootApp()` execute. No login function, render function, mutation function, persistence function, or debounce timer is stubbed.
- Supabase REST requests to the local origin are intercepted into an in-memory database with GET/POST/PATCH/DELETE behavior and `return=representation` PATCH responses. It is intentionally a stateful transport fixture, not a production-schema/RLS emulator.
- Other local assets are empty stubs; Apps Script receives an inert local response. No remote asset is fetched.
- Context routing aborts every nonlocal HTTP request, service workers are blocked, WebSockets are closed, CSP allows only local network access, and Chromium uses a dead outbound proxy plus DNS denial. The only real HTTP allowed is the exact ephemeral loopback origin.
- Each scenario gets fresh local storage and a fresh fake database. Reload and second tabs retain the scenario's local storage. A cross-tab test removes a fake remote row directly and calls the real `syncPull()`/`syncPush()` on a preloaded page to exercise reconciliation without waiting for the long production poll interval.

## Coverage

Real clicks exercise stage editing and Save in the Process rich modal; archived permanent Delete from Consulting list; batch Hide (retains a row, excludes both views); Archive modal and batch Archive; reload persistence; already-open list reconciliation; second-tab stale deletion; retained agency submission duplication for moved-Korea and deleted customers. Baseline assertions intentionally fail; the runner returns exit code 1 on any failed check/scenario.

This is UI/sync regression coverage, not authentication, asset rendering, RLS/security, full Supabase/PostgREST behavior, or live production QA. Source SHA and full request traces in JSON evidence identify precisely which concurrently edited source was exercised.
