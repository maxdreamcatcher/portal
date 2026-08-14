// substrate/events.ts
// Portal-OS v4.5 — Substrate event persistence and DO ingest handler
// Responsibilities:
// - Provide a PersistentPublisher that forwards runtime events to the Substrate DO
// - Provide a small handler (`handleIngest`) for the Substrate DO to accept events
// - Normalize events, enforce workspace routing, and persist to DO storage + KV

import { PersistentPublisher, Event as BusEvent } from '../core/eventBus'
import type { Env as WorkerEnv } from '../src/index'

// Retry/backoff helper
async function retry<T>(fn: () => Promise<T>, attempts = 3, delayMs = 200): Promise<T> {
  let lastErr: any
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn()
    } catch (err) {
      lastErr = err
      if (i < attempts - 1) await new Promise((r) => setTimeout(r, delayMs * (i + 1)))
    }
  }
  throw lastErr
}

// Small event normalization to ensure required fields exist.
export function normalizeEvent(evt: Partial<BusEvent>): BusEvent {
  const now = new Date().toISOString()
  return {
    name: (evt.name || 'substrate.event') as BusEvent['name'],
    payload: evt.payload ?? null,
    meta: evt.meta ?? {},
    timestamp: evt.timestamp ?? now,
    workspace: evt.workspace ?? 'default',
  }
}

// SubstrateDOPublisher: forwards events from the Worker runtime to the Substrate DO
export class SubstrateDOPublisher implements PersistentPublisher {
  env: WorkerEnv
  // Configure attempts/backoff if desired
  attempts: number
  delayMs: number

  constructor(env: WorkerEnv, opts?: { attempts?: number; delayMs?: number }) {
    this.env = env
    this.attempts = opts?.attempts ?? 3
    this.delayMs = opts?.delayMs ?? 200
  }

  // publish: forward the normalized event to the DO's /ingest endpoint
  async publish(rawEvt: BusEvent): Promise<void> {
    const evt = normalizeEvent(rawEvt)

    // Resolve DO id by workspace name (use default when absent)
    const name = evt.workspace || 'default'
    const id = this.env.SUBSTRATE_DO.idFromName(name)
    const stub = this.env.SUBSTRATE_DO.get(id)

    // Build request to DO ingest endpoint. We use a relative URL; the hostname
    // is ignored by Durable Object fetch; only path/method/body/headers matter.
    const req = new Request('https://internal/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(evt),
    })

    // Retry the DO fetch with backoff to tolerate transient failures
    await retry(async () => {
      const resp = await stub.fetch(req)
      if (!resp.ok) {
        const txt = await resp.text().catch(() => '')
        throw new Error(`DO ingest failed: ${resp.status} ${txt}`)
      }
    }, this.attempts, this.delayMs)
  }
}

// DO ingest handler to be called from the Substrate DO's fetch method.
// Example wiring inside the DO in src/index.ts:
//   if (url.pathname === '/ingest' && request.method === 'POST') return handleIngest(request, this.state, this.env)

export async function handleIngest(request: Request, state: DurableObjectState, env: WorkerEnv): Promise<Response> {
  try {
    if (request.headers.get('content-type')?.includes('application/json') !== true) {
      return new Response(JSON.stringify({ error: 'Invalid content-type' }), { status: 400 })
    }

    const raw = await request.json().catch(() => null)
    if (!raw) return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400 })

    const evt = normalizeEvent(raw)

    // Persist event into DO storage for fast local queries
    // Key: events:<workspace>:<timestamp>:<rand>
    const key = `events:${evt.workspace}:${evt.timestamp}:${Math.random().toString(36).slice(2, 8)}`
    await state.storage.put(key, evt)

    // Also write a compact audit record into SUBSTRATE_KV for cross-worker queries
    try {
      if (env.SUBSTRATE_KV) {
        const kvKey = `audit:${evt.workspace}:${evt.timestamp}:${Math.random().toString(36).slice(2, 8)}`
        // KV has eventual consistency; we store a compact view
        await env.SUBSTRATE_KV.put(kvKey, JSON.stringify({ name: evt.name, ts: evt.timestamp, workspace: evt.workspace }))
      }
    } catch (kvErr) {
      // non-fatal: record in DO storage an error marker
      await state.storage.put(`${key}:kv_error`, String(kvErr))
    }

    // Optionally emit an internal DO-level event that other DO handlers can watch
    // (Depending on your design, you might keep an in-memory listeners map per DO.)

    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } })
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 })
  }
}

// Utility: list events from DO storage for a workspace. This is a simple scan
// and is intentionally conservative for the scaffold. For production, add
// pagination / index structures.
export async function listEvents(state: DurableObjectState, workspace = 'default', limit = 100): Promise<BusEvent[]> {
  const out: BusEvent[] = []
  // Durable Object storage supports list() with a prefix but the types vary;
  // we use the storage.list() iterator API if available.
  try {
    // @ts-ignore - some runtimes expose state.storage.list
    if (typeof state.storage.list === 'function') {
      // Note: the iterator yields entries { key, value }
      // Use prefix: `events:${workspace}:`
      // @ts-ignore
      const it = state.storage.list({ prefix: `events:${workspace}:` })
      for await (const { key, value } of it) {
        out.push(value as BusEvent)
        if (out.length >= limit) break
      }
    } else {
      // Fallback: attempt to get a known key pattern is not feasible; return empty
      return []
    }
  } catch (err) {
    // Silently return empty on error for the scaffold
    return []
  }
  return out
}

// Integration note (how to wire this into the runtime):
// 1. In your Worker runtime (src/index.ts), attach the publisher to the event bus:
//
// import { eventBus } from './core/eventBus'
// import { SubstrateDOPublisher } from './substrate/events'
//
// eventBus.attachPersistentPublisher(new SubstrateDOPublisher(env))
//
// 2. In your Substrate DO (src/index.ts -> SubstrateDO.fetch), forward /ingest
//    requests to the handleIngest function above:
//
// import { handleIngest } from './substrate/events'
//
// if (url.pathname === '/ingest' && request.method === 'POST') {
//   return await handleIngest(request, this.state, this.env)
// }
//
// 3. Once wired, runtime calls to eventBus.emit(..., { persist: true }) will be
//    forwarded to the DO and persisted to DO storage + SUBSTRATE_KV.

// TODOs / next improvements:
// - Add schema validation (zod / ajv) for event payloads
// - Add authenticated ingest (signing or internal token) to prevent misuse
// - Improve listEvents with indexes and pagination
// - Expose DO-level subscriptions / streaming to let processes react faster
