// src/index.ts — Portal‑OS v4.5 Worker Gateway (Part 1)

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { HTTPException } from 'hono/http-exception';

// Identity physics
import { extractIdentity } from '../../identity/model';
import { applyCapabilities } from '../../identity/capabilities';

// Governance physics (namespace import to avoid named-export resolution issues)
import * as governance from '../../governance/policies';
import { applyOverrides } from '../../governance/overrides';
import { evaluateCriticality } from '../../governance/criticality';

// Routing physics
import { routeMessage } from '../../routing/router';

// Orchestration physics
import { orchestrateTask } from '../../orchestration/orchestrator';

// Substrate DO
import { SubstrateDO } from '../../src/substrate_do';
export { SubstrateDO } from '../../src/substrate_do';
// Force-export to ensure bundlers don't tree-shake the class and Wrangler can bind it
export const __EXPORTED_SUBSTRATE_DO = SubstrateDO;

export interface Env {
  KERNEL_URL: string;
  SUBSTRATE: DurableObjectNamespace;
  // ASSETS is added so the Worker can serve static assets uploaded by Wrangler Sites
  ASSETS?: any;
}

const app = new Hono<{ Bindings: Env }>();

app.use('*', cors());
// src/index.ts — Portal‑OS v4.5 Worker Gateway (Part 2)

// Core request pipeline: identity → governance → routing → kernel compute

app.post('/compute', async (c) => {
  const body = await c.req.json();

  // 1. Identity Physics
  const identity = extractIdentity(c.req, body);
  const capabilities = applyCapabilities(identity);

  // 2. Governance Physics
  const policyContext = (governance as any).applyPolicies(identity, body);
  const overrideContext = applyOverrides(identity, body);
  const criticality = evaluateCriticality(body, policyContext);

  // 3. Routing Physics
  const routed = routeMessage({
    identity,
    capabilities,
    policyContext,
    overrideContext,
    criticality,
    payload: body
  });

  // 4. Orchestration Physics
  const orchestrated = await orchestrateTask(routed);

  // 5. Forward to Kernel (/compute)
  const kernelURL = `${c.env.KERNEL_URL}/compute`;

  const kernelResponse = await fetch(kernelURL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      identity,
      governance: {
        policyContext,
        overrideContext,
        criticality
      },
      routing: routed,
      orchestration: orchestrated
    })
  });

  if (!kernelResponse.ok) {
    throw new HTTPException(500, {
      message: `Kernel error: ${kernelResponse.status}`
    });
  }

  const result = await kernelResponse.json();
  return c.json(result);
});
// src/index.ts — Portal‑OS v4.5 Worker Gateway (Part 3)

// Substrate Durable Object binding
app.post('/substrate', async (c) => {
  const id = c.env.SUBSTRATE.newUniqueId();
  const stub = c.env.SUBSTRATE.get(id);

  const body = await c.req.json();
  const response = await stub.fetch('https://do/substrate', {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json' }
  });

  const result = await response.json();
  return c.json(result);
});

// Global error handler
app.onError((err, c) => {
  console.error('Portal-OS Worker Error:', err);
  return c.json(
    {
      error: true,
      message: err.message || 'Unknown error in Portal-OS Worker'
    },
    500
  );
});

// Serve static assets and SPA fallback using Wrangler Sites ASSETS binding
app.get('*', async (c) => {
  // Try known asset binding names Wrangler might expose.
  const bindings = (c.env as any) || {};
  const assetsCandidates = [
    bindings.ASSETS,
    bindings.__STATIC_CONTENT,
    bindings.__STATIC_CONTENT_ASSETS,
    bindings.__STATIC_CONTENT_MANIFEST,
    bindings['__STATIC_CONTENT']
  ].filter(Boolean);

  // Try each available binding to fetch the asset
  for (const binding of assetsCandidates) {
    try {
      const res = await binding.fetch(c.req);
      if (res && res.status !== 404) return res;
    } catch (err) {
      // ignore and try next
      console.warn('Asset binding fetch failed, trying next binding', err);
    }
  }

  // SPA fallback: explicitly request index.html from the primary binding if possible
  try {
    const url = new URL(c.req.url);
    const indexReq = new Request(new URL('/index.html', url).toString(), c.req);
    const primary = assetsCandidates[0];
    if (primary) {
      const idx = await primary.fetch(indexReq);
      if (idx && idx.status !== 404) return idx;
    }
  } catch (e) {
    console.warn('Index fallback fetch failed', e);
  }

  // As an emergency fallback when no asset binding is available at runtime,
  // serve an embedded, minimal index.html so the SPA can bootstrap. This
  // avoids a broken root response when Cloudflare exposes the static site
  // binding under an unexpected name.
  const embeddedIndex = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portal‑OS</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;margin:0;padding:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center}.container{background:#fff;border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,.2);padding:40px;max-width:600px;text-align:center}h1{color:#333;margin:0 0 10px 0;font-size:2.5em}.version{color:#666;font-size:14px;margin-bottom:30px}.status{display:inline-block;background:#10b981;color:#fff;padding:10px 20px;border-radius:20px;font-size:14px;font-weight:600;margin-bottom:20px}</style></head><body><div class="container"><h1>🌐 Portal‑OS</h1><p class="version">Deployed (fallback)</p><div class="status">✓ Live</div></div><script>console.log('Embedded fallback index served');</script></body></html>`;

  return new Response(embeddedIndex, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
    status: 200
  });
});

// Export Worker
export default app;
