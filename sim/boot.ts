// sim/boot.ts
// Portal-OS v4.5 — SIM boot scaffold
// Responsibilities:
// - Attach SubstrateDOPublisher to eventBus so events persist to the Substrate DO
// - Load initial identity snapshot from SUBSTRATE_KV (if available)
// - Emit sim.boot.started, sim.identity.loaded, sim.context.initialized
// - Register a simple identity-sync process factory with processManager to
//   demonstrate an end-to-end flow (event -> process start -> process emits events)

import { eventBus } from '../core/eventBus'
import { processManager, type Process } from '../core/processManager'
import { SubstrateDOPublisher } from '../substrate/events'
import type { Env as WorkerEnv } from '../src/index'

export async function boot(env: WorkerEnv, opts?: { workspace?: string }) {
  const workspace = opts?.workspace ?? 'default'

  // Attach persistent publisher so future eventBus.emit(..., { persist: true })
  // will forward to the Substrate DO
  try {
    eventBus.attachPersistentPublisher(new SubstrateDOPublisher(env))
  } catch (err) {
    // Best-effort: emit an error event but continue
    await eventBus.emit({
      name: 'sim.boot.warn',
      payload: { warning: 'failed to attach SubstrateDOPublisher', error: String(err) },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: false })
  }

  // Emit sim.boot.started
  await eventBus.emit({
    name: 'sim.boot.started',
    payload: { message: 'SIM boot sequence started' },
    workspace,
    timestamp: new Date().toISOString(),
  }, { persist: true })

  // Attempt to load initial identity snapshot from SUBSTRATE_KV
  let identitySnapshot: any = null
  try {
    if (env.SUBSTRATE_KV) {
      const raw = await env.SUBSTRATE_KV.get(`identity:${workspace}`)
      if (raw) {
        try {
          identitySnapshot = JSON.parse(raw)
        } catch (err) {
          identitySnapshot = raw
        }
      }
    }
  } catch (err) {
    // Non-fatal; record a warning
    await eventBus.emit({
      name: 'sim.boot.warn',
      payload: { warning: 'failed to read SUBSTRATE_KV identity snapshot', error: String(err) },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: false })
  }

  // Emit sim.identity.loaded with what we have (may be null)
  await eventBus.emit({
    name: 'sim.identity.loaded',
    payload: { snapshot: identitySnapshot },
    workspace,
    timestamp: new Date().toISOString(),
  }, { persist: true })

  // Emit sim.context.initialized
  await eventBus.emit({
    name: 'sim.context.initialized',
    payload: { message: 'SIM context initialized', workspace },
    workspace,
    timestamp: new Date().toISOString(),
  }, { persist: true })

  // Register a basic identitySync process factory that demonstrates process lifecycle
  processManager.registerFactory('sim.identity.loaded', (evt) => {
    // Simple process impl
    const proc: Process = {
      id: `identity-sync:${evt.workspace}:${Date.now()}`,
      type: 'identity-sync',
      workspace: evt.workspace,

      async start(initialEvent) {
        // announce start (non-persistent lifecycle event)
        await eventBus.emit({
          name: 'process.identity-sync.started',
          payload: { id: this.id, initialEvent: initialEvent?.payload ?? null },
          workspace: this.workspace,
          timestamp: new Date().toISOString(),
        }, { persist: false })

        // perform a lightweight sync: for scaffold, simulate reading identity and emitting a checked event
        // In real flow: consult DO storage, compare invariants, write checkpoints
        const identity = initialEvent?.payload?.snapshot ?? null

        // Simulate processing
        await Promise.resolve()

        // Emit a result event and persist it
        await eventBus.emit({
          name: 'sim.identity.synced',
          payload: { id: this.id, identity },
          workspace: this.workspace,
          timestamp: new Date().toISOString(),
        }, { persist: true })
      },

      async onEvent(e) {
        // React to subsequent identity updates
        // For scaffold, if we get an updated snapshot, emit a checkpoint
        if (e.name === 'sim.identity.updated') {
          await eventBus.emit({
            name: 'process.identity-sync.update.received',
            payload: { id: this.id, update: e.payload },
            workspace: this.workspace,
            timestamp: new Date().toISOString(),
          }, { persist: false })

          // optionally persist a checkpoint event
          await eventBus.emit({
            name: 'sim.identity.synced',
            payload: { id: this.id, identity: e.payload },
            workspace: this.workspace,
            timestamp: new Date().toISOString(),
          }, { persist: true })
        }
      },

      async stop(reason) {
        await eventBus.emit({
          name: 'process.identity-sync.stopped',
          payload: { id: this.id, reason },
          workspace: this.workspace,
          timestamp: new Date().toISOString(),
        }, { persist: false })
      },

      async status() {
        return { id: this.id, type: this.type, workspace: this.workspace, running: true }
      },
    }
    return proc
  })

  // Return a small status object for the caller
  return { ok: true, workspace, identityLoaded: !!identitySnapshot }
}

export default { boot }
