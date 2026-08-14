// sim/identitySyncProcess.ts
// Portal-OS v4.5 — Identity Sync Process
// A concrete Process implementation for identity synchronization.
// Designed to be produced by a factory: createIdentitySyncProcess(evt)

import { eventBus } from '../core/eventBus'
import type { Process } from '../core/processManager'
import type { Event } from '../core/eventBus'

export function createIdentitySyncProcess(evt: Event): Process {
  const workspace = evt.workspace || 'default'
  const startTs = Date.now()
  let running = true
  let lastSnapshot: any = evt.payload?.snapshot ?? null

  const id = `identity-sync:${workspace}:${startTs}`

  async function start(initialEvent?: Event) {
    // Announce start (non-persistent)
    await eventBus.emit({
      name: 'process.identity-sync.started',
      payload: { id, initialEvent: initialEvent?.payload ?? null },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: false })

    // Perform initial synchronization work.
    // In this scaffold we just emit a synced event with the snapshot we have.
    await emitSynced(lastSnapshot)
  }

  async function onEvent(e: Event) {
    // Handle subsequent identity updates
    if (e.name === 'sim.identity.updated') {
      // Update in-memory snapshot
      lastSnapshot = e.payload

      // Acknowledge receipt (non-persistent)
      await eventBus.emit({
        name: 'process.identity-sync.update.received',
        payload: { id, update: e.payload },
        workspace,
        timestamp: new Date().toISOString(),
      }, { persist: false })

      // Persist a synced event representing the new canonical snapshot
      await emitSynced(lastSnapshot)
    }
  }

  async function stop(reason?: string) {
    running = false
    await eventBus.emit({
      name: 'process.identity-sync.stopped',
      payload: { id, reason },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: false })
  }

  async function checkpoint() {
    // Emit a checkpoint event (persisted) so other components can see progress
    await eventBus.emit({
      name: 'process.identity-sync.checkpoint',
      payload: { id, snapshot: lastSnapshot },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: true })
  }

  async function status() {
    return {
      id,
      type: 'identity-sync',
      workspace,
      running,
      lastSnapshotPresent: !!lastSnapshot,
      uptimeMs: Date.now() - startTs,
    }
  }

  async function emitSynced(snapshot: any) {
    await eventBus.emit({
      name: 'sim.identity.synced',
      payload: { id, snapshot },
      workspace,
      timestamp: new Date().toISOString(),
    }, { persist: true })
  }

  const proc: Process = {
    id,
    type: 'identity-sync',
    workspace,
+   criticality: 'medium',
    start,
    onEvent,
    stop,
    checkpoint,
    status,
  }

  return proc
}
