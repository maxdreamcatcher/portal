// tests/admin.criticality.override.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import app from '../src/index'
import { createTestEnv } from './setup'
import { getCriticalityForType } from '../governance/criticalityRegistry'

describe('admin criticality override endpoint', () => {
  let env: any
  beforeEach(() => {
    env = createTestEnv()
  })

  it('requires admin auth and returns unauthorized without secret', async () => {
    const req = new Request('https://example.com/admin/policies/criticality/override', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'unknown.type', criticality: 'critical' }) })
    const resp = await (app as any).fetch(req, env)
    expect(resp.status).toBe(401)
    const txt = await resp.text()
    expect(txt).toContain('unauthorized')
  })

  it('registers override, persists audit to KV, and updates registry', async () => {
    const payload = { type: 'unknown.type', criticality: 'critical' }
    const req = new Request('https://example.com/admin/policies/criticality/override', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-portal-admin': 'test-secret' }, body: JSON.stringify(payload) })
    const resp = await (app as any).fetch(req, env)
    expect(resp.status).toBe(200)
    const body = await resp.json()
    expect(body.ok).toBe(true)
    expect(body.type).toBe(payload.type)
    expect(body.criticality).toBe(payload.criticality)

    // registry should reflect override immediately
    expect(getCriticalityForType('unknown.type')).toBe('critical')

    // KV should contain an audit entry for the override
    const kv: any = env.SUBSTRATE_KV
    const prefix = `gov:config:criticality:override:${encodeURIComponent(payload.type)}:`
    let found = false
    // iterate pages
    for await (const page of kv.list({ prefix })) {
      for (const item of page) {
        if (item.name && item.value) {
          const v = JSON.parse(item.value)
          if (v && v.action === 'registerOverride' && v.type === payload.type && v.criticality === payload.criticality) {
            found = true
            break
          }
        }
      }
      if (found) break
    }
    expect(found).toBe(true)
  })

  it('validates request body', async () => {
    const req = new Request('https://example.com/admin/policies/criticality/override', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-portal-admin': 'test-secret' }, body: JSON.stringify({ foo: 'bar' }) })
    const resp = await (app as any).fetch(req, env)
    expect(resp.status).toBe(400)
    const body = await resp.json()
    expect(body.ok).toBe(false)
  })
})
