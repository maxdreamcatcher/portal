// governance/config.ts
// Portal-OS v4.5 — KV-backed governance config persistence

import { setBlockedWorkspaces, setMaintenanceWindow, setToolInvocationRequireApproval } from './policies'
import { eventBus } from '../core/eventBus'
import type { Env } from '../src/index'

const KEY_BLOCKED = 'gov:config:block-workspaces'
const KEY_MAINT = 'gov:config:maintenance-window'
const KEY_TOOL = 'gov:config:tool-approval'
const KEY_STRICT_MAINT = 'gov:config:maintenance-strict'

// Helpers to read/write to SUBSTRATE_KV
export async function getBlockedWorkspaces(env: Env): Promise<string[]> {
  if (!env.SUBSTRATE_KV) return []
  const raw = await env.SUBSTRATE_KV.get(KEY_BLOCKED)
  if (!raw) return []
  try { return JSON.parse(raw) } catch { return [] }
}

export async function setBlockedWorkspacesKV(env: Env, list: string[]): Promise<void> {
  if (env.SUBSTRATE_KV) {
    await env.SUBSTRATE_KV.put(KEY_BLOCKED, JSON.stringify(list))
    // also write a compact audit entry
    try {
      const ts = new Date().toISOString()
      await env.SUBSTRATE_KV.put(`audit:config:block:${ts}`, JSON.stringify({ action: 'setBlockedWorkspaces', list, ts }))
    } catch (_) {}
  }
  // Apply to in-memory knobs
  setBlockedWorkspaces(list)
  // notify runtime (bypass governance to avoid policy blocking)
  try {
    await eventBus.emit({ name: 'governance.config.updated', payload: { key: 'blockedWorkspaces', value: list }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: false })
  } catch (_) {}
}

export async function getMaintenanceWindow(env: Env): Promise<{ startHour: number; endHour: number } | null> {
  if (!env.SUBSTRATE_KV) return null
  const raw = await env.SUBSTRATE_KV.get(KEY_MAINT)
  if (!raw) return null
  try { return JSON.parse(raw) } catch { return null }
}

export async function setMaintenanceWindowKV(env: Env, startHour: number | null, endHour: number | null): Promise<void> {
  if (env.SUBSTRATE_KV) {
    if (startHour === null || endHour === null) {
      await env.SUBSTRATE_KV.delete(KEY_MAINT)
    } else {
      await env.SUBSTRATE_KV.put(KEY_MAINT, JSON.stringify({ startHour, endHour }))
    }
    // audit
    try {
      const ts = new Date().toISOString()
      await env.SUBSTRATE_KV.put(`audit:config:maintenance:${ts}`, JSON.stringify({ action: 'setMaintenanceWindow', startHour, endHour, ts }))
    } catch (_) {}
  }

  // Apply in-memory
  if (startHour === null || endHour === null) setMaintenanceWindow(null as any, null as any)
  else setMaintenanceWindow(startHour, endHour)

  try {
    await eventBus.emit({ name: 'governance.config.updated', payload: { key: 'maintenanceWindow', value: startHour === null ? null : { startHour, endHour } }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: false })
  } catch (_) {}
}

export async function getToolInvocationRequireApproval(env: Env): Promise<boolean> {
  if (!env.SUBSTRATE_KV) return true
  const raw = await env.SUBSTRATE_KV.get(KEY_TOOL)
  if (!raw) return true
  try { return JSON.parse(raw) as boolean } catch { return true }
}

export async function setToolInvocationRequireApprovalKV(env: Env, requireApproval: boolean): Promise<void> {
  if (env.SUBSTRATE_KV) {
    await env.SUBSTRATE_KV.put(KEY_TOOL, JSON.stringify(requireApproval))
    try {
      const ts = new Date().toISOString()
      await env.SUBSTRATE_KV.put(`audit:config:tool:${ts}`, JSON.stringify({ action: 'setToolInvocationRequireApproval', requireApproval, ts }))
    } catch (_) {}
  }
  // Apply in-memory
  setToolInvocationRequireApproval(requireApproval)
  try {
    await eventBus.emit({ name: 'governance.config.updated', payload: { key: 'toolInvocationRequireApproval', value: requireApproval }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: false })
  } catch (_) {}
}

export async function getStrictMaintenanceFlag(env: Env): Promise<boolean> {
  if (!env.SUBSTRATE_KV) return false
  const raw = await env.SUBSTRATE_KV.get(KEY_STRICT_MAINT)
  if (!raw) return false
  try { return JSON.parse(raw) as boolean } catch { return false }
}

export async function setStrictMaintenanceFlagKV(env: Env, v: boolean): Promise<void> {
  if (env.SUBSTRATE_KV) {
    await env.SUBSTRATE_KV.put(KEY_STRICT_MAINT, JSON.stringify(v))
    try {
      const ts = new Date().toISOString()
      await env.SUBSTRATE_KV.put(`audit:config:maintenance-strict:${ts}`, JSON.stringify({ action: 'setStrictMaintenance', v, ts }))
    } catch (_) {}
  }
  try {
    await eventBus.emit({ name: 'governance.config.updated', payload: { key: 'maintenanceStrict', value: v }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: false })
  } catch (_) {}
}

// Load config from KV and apply to in-memory knobs
export async function loadGovernanceConfig(env: Env) {
  try {
    const blocked = await getBlockedWorkspaces(env)
    setBlockedWorkspaces(blocked)
    const maint = await getMaintenanceWindow(env)
    if (maint) setMaintenanceWindow(maint.startHour, maint.endHour)
    const tool = await getToolInvocationRequireApproval(env)
    setToolInvocationRequireApproval(tool)

    // Emit a config.loaded event (bypass governance to avoid self-evaluation)
    await eventBus.emit({ name: 'governance.config.loaded', payload: { blocked, maintenance: maint, tool }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: true })
    return { blocked, maintenance: maint, tool }
  } catch (err) {
    // best-effort: emit a non-persistent warning
    try {
      await eventBus.emit({ name: 'governance.config.load.failed', payload: { error: String(err) }, workspace: 'default', timestamp: new Date().toISOString(), meta: { __bypass_governance: true } as any }, { persist: false })
    } catch (_) {}
    return null
  }
}
