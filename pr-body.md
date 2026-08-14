## chore: set RUNTIME_KV namespace id

This PR replaces the placeholder RUNTIME_KV namespace IDs in wrangler.toml with the provided namespace id.

What I changed
- Replaced both occurrences of the RUNTIME_KV placeholder in wrangler.toml with `b9134f2c8d7e4a0fb2c1d9e6a4f7b812`.

Commit: 9fa39fa2683bde40f5efd064b8adb88360a142e7
Branch: update/runtime-kv-id

Verification checklist (maintainer)
- Run:
  - npm ci
  - npm run build
  - ls -l dist/worker.js  # confirm the worker bundle path matches wrangler.toml
- Confirm Durable Object class
  - grep -R "class SubstrateDO" -n src || rg "class SubstrateDO" src
  - Ensure SubstrateDO is exported: export class SubstrateDO { ... }
- Wrangler publish dry-run
  - wrangler publish --dry-run

Notes
- Cloudflare KV validation was intentionally skipped per request.
- If you want me to validate KV IDs against Cloudflare, provide an account-scoped API token and I will run the checks.
