# Portal‑OS v1 Deployment Checklist

Author: Max
Date: 2026-08-12

## ⭐ Portal‑OS v1 Deployment Checklist (Top Level)

1. **Update KV IDs**  
   - Replace both `RUNTIME_KV` entries with **b9134f2c8d7e4a0fb2c1d9e6a4f7b812**  
   - Confirm `SUBSTRATE_KV` is correct.

2. **Fix Worker entrypoint**  
   - Ensure `main = "dist/worker.js"` is the *only* entrypoint.  
   - Remove any top‑level `main = "src/index.ts"`.

3. **Verify DO migration block**  
   - `tag = "v1"`  
   - `new_classes = ["SubstrateDO"]`

4. **Ensure Portal‑OS runtime is in dist/worker.js**  
   - Quick Edit → paste runtime → save → confirm build outputs to dist/worker.js.

5. **Run build**  
   - `npm run build`  
   - Confirm dist/worker.js exists.

6. **Publish Worker**  
   - `npx wrangler publish --config wrangler.toml`

7. **Verify live endpoints**  
   - `/` → Portal‑OS status JSON  
   - `/tick` → runtime tick  
   - `/kv/<key>` → KV read  
   - DO PUT/GET → substrate storage

8. **Verify bindings in Cloudflare dashboard**  
   - SUBSTRATE_KV  
   - RUNTIME_KV  
   - SUBSTRATE_DO

9. **Verify production environment**  
   - Ensure production env mirrors default bindings.

10. **Merge PR → deploy → confirm runtime stability**

---

## ⭐ Full Expanded Checklist (Detailed)

### 1. KV Namespace IDs
- Replace both `RUNTIME_KV` entries with:  
  `b9134f2c8d7e4a0fb2c1d9e6a4f7b812`
- Confirm `SUBSTRATE_KV` is:  
  `807456cb41558d3c820308b20affa851`

### 2. TOML Entrypoint Correction
Your TOML must contain **only**:

```
[worker]
main = "dist/worker.js"
```

Remove:

```
main = "src/index.ts"
```

This is critical — Cloudflare cannot deploy two entrypoints.

### 3. Durable Object Migration
Ensure:

```
[[migrations]]
tag = "v1"
new_classes = ["SubstrateDO"]
```

This creates the DO storage.

### 4. Worker Runtime Placement
Your Portal‑OS runtime must be in:

```
dist/worker.js
```

If Quick Edit is used, ensure the build process copies the runtime into dist/worker.js.

### 5. Build
Run:

```
npm run build
```

Confirm:

```
dist/worker.js
```

exists and contains the Portal‑OS runtime.

### 6. Publish
Run:

```
npx wrangler publish --config wrangler.toml
```

This deploys:

- KV bindings  
- DO bindings  
- Migrations  
- Worker runtime  

### 7. Live Endpoint Verification
Check:

- `/` → Portal‑OS status JSON
- `/tick` → runtime tick
- `/kv/<key>` → KV read
- DO PUT/GET → substrate storage

### 8. Cloudflare Dashboard Verification
In **Workers & Pages → portal-os-v1 → Settings → Bindings**:

- SUBSTRATE_KV
- RUNTIME_KV
- SUBSTRATE_DO

All must appear.

### 9. Production Environment
Ensure:

```
[env.production]
name = "portal-os-v1-prod"
```

And both KV namespaces + DO bindings are mirrored.

### 10. Merge PR → Deploy → Confirm Stability
After merging:

- Re-run publish
- Confirm runtime stability
- Confirm DO storage persists
- Confirm KV writes/reads
- Confirm routing
- Confirm no fallback to “hello world”

---

## Guided Links for next steps
- Deploy Portal‑OS v1
- Verify Worker bindings
- Check live endpoints

If you want, I can also generate:
- A post‑merge activation checklist
- A runtime smoke test suite
- A Portal‑OS v1 health dashboard JSON schema
