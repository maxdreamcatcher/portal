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

// Export Worker
export default app;
