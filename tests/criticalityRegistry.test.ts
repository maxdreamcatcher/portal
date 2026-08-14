// tests/criticalityRegistry.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { getCriticalityForType, registerOverride } from '../governance/criticalityRegistry'
import { processManager } from '../core/processManager'
import { createTestEnv } from './setup'
import { eventBus } from '../core/eventBus'

describe('criticality registry', () => {
  let env: any
  beforeEach(() => {
    env = createTestEnv()
    processManager.resetForTests()
  })

  it('returns canonical mappings and prefix matches', () => {
    expect(getCriticalityForType('sim.boot')).toBe('critical')
    expect(getCriticalityForType('sim.identity.physics.update')).toBe('critical') // prefix match
    expect(getCriticalityForType('identity-sync')).toBe('medium')
    expect(getCriticalityForType('tec.tool.invoked')).toBe('non-critical')
    expect(getCriticalityForType('unknown.type')).toBe('non-critical') // fallback
  })

  it('allows runtime overrides and ProcessManager uses registry defaults', async () => {
    // override unknown.type to critical
    registerOverride('unknown.type', 'critical')
    expect(getCriticalityForType('unknown.type')).toBe('critical')

    // Verify ProcessManager picks up registry default when factory doesn't set criticality
    processManager.registerFactory('proc.infer', (evt: any) => {
      const id = `inf:${Date.now()}`
      const proc = {
        id,
        type: 'identity-sync', // canonical mapping => medium
        workspace: evt.workspace || 'default',
        // NO explicit criticality
        async start() {},
        async onEvent() {},
        async stop() {},
        async status() { return { id } }
      }
      return proc
    })

    await eventBus.emit({ name: 'proc.infer', payload: {}, workspace: 'w-test', timestamp: new Date().toISOString() } as any, { persist: false })
    // allow startup
    await new Promise(r => setTimeout(r, 20))

    const active = processManager.listActive()
    const p = active.find(a => a.type === 'identity-sync')
    expect(p).toBeTruthy()
    expect(p?.criticality).toBe('medium')
  })
})
