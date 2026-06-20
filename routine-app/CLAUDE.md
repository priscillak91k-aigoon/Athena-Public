# Project Context

LifeHub (aka "Symphony 2.0") — personal life management web app.
Currently mid-migration: legacy Supabase-backed codebase → Express + SQLite backend.
Hosted on a local Atom Workstation (Gigabyte AI TOP / ARM64), accessed remotely via Tailscale.
No public internet exposure — Tailscale is the only access path. Treat any code that
assumes public-internet auth flows (e.g. OAuth redirect URLs, CORS for arbitrary
origins) as a smell and flag it.

A second related project, **Hawkeye**, is an automated architectural plan compliance
tool: scans PDF plans, pre-empts council RFIs. Separate repo/context — only relevant
if explicitly working in that directory.

## Stack

- **Backend**: Express + SQLite (`server/` directory). Some legacy Supabase code may still exist mid-migration — check before assuming which backend a given route uses.
- **Frontend**: Vanilla HTML, CSS, JavaScript. No build step, no frontend frameworks (no React/Vue).
- **Hosting**: Local Atom Workstation, remote access via Tailscale only. Caddy proxy handles routing.
- **Environment**: Node.js v24.14, package manager is `npm` (backend only).

## Commands

- `cd server && node server.js` — Start the Express API backend.
- Frontend does not require a build step; served statically.
- `cd server && npm install` — Install backend dependencies.

## Migration rules (Supabase → Express + SQLite)

- Don't assume Supabase's built-in auth/RLS patterns translate directly — SQLite has
  no row-level security; access control must be enforced explicitly in route handlers.
- Migrate one table/feature at a time. Preserve existing behavior unless told otherwise.
- Flag anywhere the old code relied on Supabase-specific features (realtime
  subscriptions, storage buckets, edge functions) before assuming a 1:1 replacement.
- Security matters here more than usual: this app handles personal life-management
  data. Treat input validation and auth checks as required, not optional, even for
  Tailscale-only routes.

## Code style

- **Frontend**: Vanilla ES6+ JS. No bundlers.
- **Backend**: Node CommonJS (`require()`).
- **Formatting**: Keep files strictly modular. Separate concerns (Anti-Spaghetti Protocol).
- **Conventions**: No enforced linters, but write clean, explicit code with low cyclomatic complexity.

## Workflow

- **Cache-Buster Veto**: Always bump the query parameter (`?v=...`) on JS/CSS imports in `index.html` after making frontend changes. Browsers will silently load stale cache otherwise.
- Run typecheck and tests before considering a change done.
- For schema changes, show the migration before applying it — don't run destructive
  SQLite operations without confirmation.
- When compacting, always preserve the list of modified files and any test commands
  used, plus the current migration status (which tables/features are done vs pending).

## Collaboration note

This project is also built in part with another AI assistant ("Lobotto"). Code you
encounter may have been written by it — review for correctness rather than assuming
it follows your conventions. If something looks fragile or inconsistent with the
rest of the codebase, flag it rather than silently matching the pattern. Lobotto is designed to be highly combative and structural; expect clinical precision.
