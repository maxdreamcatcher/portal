// governance/admin.ts
// Portal-OS v4.5 — Admin endpoints for governance (KV-backed)
// - GET  /admin/policies                 -> list registered policies and runtime knobs
// - POST /admin/policies/block-workspaces -> set blocked workspaces (writes to KV)
// - POST /admin/policies/maintenance     -> set/clear maintenance window (writes to KV)
// - POST /admin/policies/tool-approval   -> toggle tool invocation approval requirement (writes to KV)
// - GET  /admin/policies/audit-log       -> list recent governance.audit entries from SUBSTRATE_KV
// - GET  /admin/policies/criticality     -> list canonical criticality mappings + runtime overrides
// - POST /admin/policies/criticality/override -> register a runtime override (persist to KV + audit)

import { Router } from 'hono'
import type { Env } from '../src/index'
import { policyRegistry } from './policies'
import { listMappings, registerOverride } from './criticalityRegistry'

const admin = new Router()

// Simple middleware to guard admin routes. In production replace with a proper auth check.
admin.use('*', async (c, next) => {
  const secret = c.req.header('x-portal-admin') || c.req.query('admin_secret')
  // If a secret is configured via env (SUBSTRATE_ADMIN_SECRET), require it.
  const expected = (c.env as unknown as Env)['SUBSTRATE_ADMIN_SECRET'] as string | undefined
  if (expected) {
    if (!secret || secret !== expected) return c.text('unauthorized', 401)
  }
  // Otherwise, allow local access in dev
  await next()
})

// GET /admin/policies
admin.get('/policies', async (c) => {
  const env = c.env as unknown as Env
  const list = policyRegistry.list().map((p) => ({ id: p.id, description: p.description, priority: p.priority }))

  // Read current knobs from KV-backed config module
  try {
    const cfg = await import('./config')
    const blocked = await cfg.getBlockedWorkspaces(env)
    const maintenance = await cfg.getMaintenanceWindow(env)
    const tool = await cfg.getToolInvocationRequireApproval(env)
    return c.json({ ok: true, policies: list, knobs: { blockedWorkspaces: blocked, maintenance, tool } })
  } catch (err) {
    // Fall back to in-memory view if KV unavailable
    return c.json({ ok: true, policies: list, knobs: { blockedWorkspaces: [], maintenance: null, tool: true }, warning: String(err) })
  }
})

// GET /admin/policies/criticality
admin.get('/policies/criticality', async (c) => {
  try {
    const mappings = listMappings()
    return c.json({ ok: true, mappings })
  } catch (err) {
    return c.json({ ok: false, error: String(err) }, 500)
  }
})

// POST /admin/policies/criticality/override
// Body: { type: string, criticality: 'critical'|'medium'|'non-critical' }
// This registers a runtime override in the in-memory registry and persists an audit entry to SUBSTRATE_KV when available.
admin.post('/policies/criticality/override', async (c) => {
  const env = c.env as unknown as Env
  const body = await c.req.json().catch(() => null)
  if (!body || typeof body.type !== 'string' || typeof body.criticality !== 'string') return c.json({ ok: false, error: 'invalid body' }, 400)
  const { type, criticality } = body as { type: string; criticality: 'critical' | 'medium' | 'non-critical' }
  if (!['critical', 'medium', 'non-critical'].includes(criticality)) return c.json({ ok: false, error: 'invalid criticality' }, 400)

  // Register in-memory override immediately
  try {
    registerOverride(type, criticality as any)
  } catch (err) {
    return c.json({ ok: false, error: 'failed to register override: ' + String(err) }, 500)
  }

  // Persist audit entry to SUBSTRATE_KV if bound
  if (env.SUBSTRATE_KV) {
    try {
      const ts = new Date().toISOString()
      const key = `gov:config:criticality:override:${encodeURIComponent(type)}:${ts}`
      await env.SUBSTRATE_KV.put(key, JSON.stringify({ action: 'registerOverride', type, criticality, ts }))
      // also store a compact mapping entry for quick lookup (optional)
      try {
        await env.SUBSTRATE_KV.put(`gov:config:criticality:overrides`, JSON.stringify({ type, criticality, ts }))
      } catch (_) {}
    } catch (err) {
      // Non-fatal: return success but include warning
      return c.json({ ok: true, warning: 'override registered in-memory but failed to persist audit: ' + String(err), type, criticality })
    }
  }

  return c.json({ ok: true, type, criticality })
})

// POST /admin/policies/block-workspaces
admin.post('/policies/block-workspaces', async (c) => {
  const env = c.env as unknown as Env
  const body = await c.req.json().catch(() => null)
  if (!body || !Array.isArray(body.blocked)) return c.json({ ok: false, error: 'invalid body' }, 400)
  // Persist to KV and update in-memory
  try {
    const cfg = await import('./config')
    await cfg.setBlockedWorkspacesKV(env, body.blocked)
    return c.json({ ok: true, blocked: body.blocked })
  } catch (err) {
    return c.json({ ok: false, error: String(err) }, 500)
  }
})

// POST /admin/policies/maintenance
admin.post('/policies/maintenance', async (c) => {
  const env = c.env as unknown as Env
  const body = await c.req.json().catch(() => null)
  if (!body) return c.json({ ok: false, error: 'invalid body' }, 400)
  const { startHour, endHour } = body
  if (startHour === null || endHour === null) {
    try {
      const cfg = await import('./config')
      await cfg.setMaintenanceWindowKV(env, null as any, null as any)
      return c.json({ ok: true, maintenance: null })
    } catch (err) {
      return c.json({ ok: false, error: String(err) }, 500)
    }
  }
  if (typeof startHour !== 'number' || typeof endHour !== 'number') return c.json({ ok: false, error: 'invalid hours' }, 400)
  try {
    const cfg = await import('./config')
    await cfg.setMaintenanceWindowKV(env, startHour, endHour)
    return c.json({ ok: true, maintenance: { startHour, endHour } })
  } catch (err) {
    return c.json({ ok: false, error: String(err) }, 500)
  }
})

// POST /admin/policies/tool-approval
admin.post('/policies/tool-approval', async (c) => {
  const env = c.env as unknown as Env
  const body = await c.req.json().catch(() => null)
  if (!body || typeof body.requireApproval !== 'boolean') return c.json({ ok: false, error: 'invalid body' }, 400)
  try {
    const cfg = await import('./config')
    await cfg.setToolInvocationRequireApprovalKV(env, body.requireApproval)
    return c.json({ ok: true, requireApproval: body.requireApproval })
  } catch (err) {
    return c.json({ ok: false, error: String(err) }, 500)
  }
})

// GET /admin/policies/audit-log
admin.get('/policies/audit-log', async (c) => {
  const env = c.env as unknown as Env
  const workspace = c.req.query('workspace') || 'default'
  // Read recent audit entries from SUBSTRATE_KV. We assume keys like audit:<workspace>:<ts>...
  if (!env.SUBSTRATE_KV) return c.json({ ok: false, error: 'SUBSTRATE_KV not bound' }, 500)

  // This is a simple scan: in production, use a structured index or pagination
  const prefix = `audit:${workspace}:`
  const items: Array<{ key: string; value: string }> = []
  try {
    // @ts-ignore kv.list is available in some Workers runtimes; if unavailable, return a not-implemented response
    if (typeof (env.SUBSTRATE_KV as any).list === 'function') {
      // list pages through results (limit to 100)
      // @ts-ignore
      const iter = (env.SUBSTRATE_KV as any).list({ prefix })
      for await (const page of iter) {
        for (const r of page) {
          items.push({ key: r.name || r.key || 'unknown', value: r.value || r.body || '' })
          if (items.length >= 100) break
        }
        if (items.length >= 100) break
      }
    } else {
      return c.json({ ok: false, error: 'KV list not supported in this runtime' }, 501)
    }
  } catch (err) {
    return c.json({ ok: false, error: String(err) }, 500)
  }

  return c.json({ ok: true, items })
})

export const adminRouter = admin
