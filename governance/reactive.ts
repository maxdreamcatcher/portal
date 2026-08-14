// governance/reactive.ts
// Portal-OS v4.5 — Reactive governance propagation
// Listens for governance.config.loaded and governance.config.updated events
// and applies governance pressure to runtime components (ProcessManager, etc.).

import { eventBus } from '../core/eventBus'
import { processManager } from '../core/processManager'
import type { Event } from '../core/eventBus'

async function applyGovernance(payload: any) {
  try {
    const blocked: string[] = payload?.blocked ?? []
    const maintenance = payload?.maintenance ?? null

    // 1) Stop processes in blocked workspaces
    if (Array.isArray(blocked) && blocked.length > 0) {
      const active = processManager.listActive()
      for (const p of active) {
        if (blocked.includes(p.workspace)) {
          try {
            await processManager.stopProcess(p.id)
          } catch (err) {
            // best-effort: emit a warning
            try {
              await eventBus.emit({
                name: 'governance.reactive.warn',
                payload: { error: String(err), id: p.id, workspace: p.workspace },
                workspace: p.workspace,
                timestamp: new Date().toISOString(),
              }, { persist: false })
            } catch (_) {}
          }
        }
      }
    }

    // 2) If maintenance window is active, stop non-critical processes
    if (maintenance && maintenance.startHour !== undefined && maintenance.endHour !== undefined) {
      const hour = new Date().getUTCHours()
      const { startHour, endHour } = maintenance
      const inWindow = startHour <= endHour ? hour >= startHour && hour < endHour : hour >= startHour || hour < endHour
      if (inWindow) {
        const active = processManager.listActive()
        for (const p of active) {
          try {
            await processManager.stopProcess(p.id)
          } catch (err) {
            try { await eventBus.emit({ name: 'governance.reactive.warn', payload: { error: String(err), id: p.id }, workspace: p.workspace, timestamp: new Date().toISOString() }, { persist: false }) } catch (_) {}
          }
        }
      }
    }

    // Emit a lightweight reactive.applied event (non-persistent)
    try {
      await eventBus.emit({
        name: 'governance.reactive.applied',
        payload: { applied: true, payload },
        workspace: 'default',
        timestamp: new Date().toISOString(),
      }, { persist: false })
    } catch (_) {}
  } catch (err) {
    try {
      await eventBus.emit({ name: 'governance.reactive.error', payload: { error: String(err) }, workspace: 'default', timestamp: new Date().toISOString() }, { persist: false })
    } catch (_) {}
  }
}

// React to config load and updates
eventBus.on('governance.config.loaded', async (evt: Event) => {
  await applyGovernance(evt.payload)
})

eventBus.on('governance.config.updated', async (evt: Event) => {
  await applyGovernance(evt.payload)
})

// Also expose a manual apply function for admin or tests
export async function applyCurrentGovernance(payload?: any) {
  if (!payload) return
  return applyGovernance(payload)
}
