// tests/processManager.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { processManager } from '../core/processManager'
import { eventBus } from '../core/eventBus'
import { createTestEnv } from './setup'

describe('ProcessManager - basic lifecycle', () => {
  let env: any

  beforeEach(() => {
    env = createTestEnv()
  })

  afterEach(async () => {
    // stop all active processes
    const active = processManager.listActive()
    for (const p of active) {
      await processManager.stopProcess(p.id)
    }
  })

  it('starts a process via factory and stops it', async () => {
    // register factory
    processManager.registerFactory('test.start', (evt) => {
      const workspace = evt.workspace || 'default'
      const id = `test:${workspace}:${Date.now()}`
      let started = false
      let stopped = false
      const proc = {
        id,
        type: 'test-process',
        workspace,
        criticality: 'non-critical' as any,
        async start(initialEvent?: any) { started = true },
        async onEvent(_evt: any) {},
        async stop(_reason?: string) { stopped = true },
        async status() { return { id, started, stopped } }
      }
      return proc
    })

    const ev = { name: 'test.start', payload: {}, workspace: 'w1', timestamp: new Date().toISOString() }
    await eventBus.emit(ev as any, { persist: false })

    // allow loop to process
    await new Promise((r) => setTimeout(r, 10))

    const active = processManager.listActive()
    expect(active.length).toBe(1)
    const p = active[0]

    // now stop by id
    await processManager.stopProcess(p.id)
    const after = processManager.listActive()
    expect(after.length).toBe(0)
  })
})
