// tests/governance.reactive.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { createTestEnv } from './setup'
import { eventBus } from '../core/eventBus'
import { processManager } from '../core/processManager'
import { setBlockedWorkspacesKV, setMaintenanceWindowKV, setStrictMaintenanceFlagKV } from '../governance/config'

describe('governance/reactive selective termination', () => {
  let env: any
  beforeEach(() => {
    env = createTestEnv()
  })

  afterEach(async () => {
    // cleanup processes
    const active = processManager.listActive()
    for (const p of active) await processManager.stopProcess(p.id)
  })

  it('stops non-critical processes on workspace block but keeps medium', async () => {
    // register a generic factory that sets criticality from payload
    processManager.registerFactory('proc.start', (evt: any) => {
      const workspace = evt.workspace || 'default'
      const id = `proc:${workspace}:${evt.payload.type}:${Date.now()}`
      const crit = evt.payload.type === 'medium' ? 'medium' : 'non-critical'
      let running = false
      const proc = {
        id,
        type: `proc-${evt.payload.type}`,
        workspace,
        criticality: crit as any,
        async start() { running = true },
        async onEvent() {},
        async stop() { running = false },
        async status() { return { id, running } }
      }
      return proc
    })

    // start a non-critical and a medium process
    await eventBus.emit({ name: 'proc.start', payload: { type: 'non' }, workspace: 'w1', timestamp: new Date().toISOString() } as any, { persist: false })
    await eventBus.emit({ name: 'proc.start', payload: { type: 'medium' }, workspace: 'w1', timestamp: new Date().toISOString() } as any, { persist: false })

    await new Promise(r => setTimeout(r, 20))
    let active = processManager.listActive()
    // both started
    expect(active.find(a => a.type.includes('non'))).toBeTruthy()
    expect(active.find(a => a.type.includes('medium'))).toBeTruthy()

    // block workspace — non-critical should stop
    await setBlockedWorkspacesKV(env, ['w1'])
    await new Promise(r => setTimeout(r, 20))

    active = processManager.listActive()
    expect(active.find(a => a.type.includes('non'))).toBeFalsy()
    expect(active.find(a => a.type.includes('medium'))).toBeTruthy()
  })

  it('strict maintenance stops medium processes as well', async () => {
    // start a medium process
    processManager.registerFactory('proc.start2', (evt: any) => {
      const workspace = evt.workspace || 'default'
      const id = `proc2:${workspace}:${Date.now()}`
      const proc = {
        id,
        type: 'proc-medium',
        workspace,
        criticality: 'medium' as any,
        async start() {},
        async onEvent() {},
        async stop() {},
        async status() { return { id } }
      }
      return proc
    })

    await eventBus.emit({ name: 'proc.start2', payload: {}, workspace: 'w2', timestamp: new Date().toISOString() } as any, { persist: false })
    await new Promise(r => setTimeout(r, 20))
    let active = processManager.listActive()
    expect(active.find(a => a.type === 'proc-medium')).toBeTruthy()

    // enable strict and set maintenance window that includes current hour
    await setStrictMaintenanceFlagKV(env, true)
    await setMaintenanceWindowKV(env, 0, 23)
    await new Promise(r => setTimeout(r, 20))

    active = processManager.listActive()
    expect(active.find(a => a.type === 'proc-medium')).toBeFalsy()
  })
})
