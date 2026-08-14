// governance/policies.ts
// Portal-OS v4.5 — Governance policy registry and runtime enforcement
// Responsibilities:
// - Provide a registry for named policies
// - Evaluate policies per-event and produce allow/block decisions
// - Emit governance audit events (persisted) when policies run
// - Install a lightweight interception layer on eventBus.emit so policies
//   can block or annotate events before they reach consumers (ProcessManager, etc.)

import { eventBus, type Event } from '../core/eventBus'

export type PolicyResult =
  | { allowed: true; metadata?: Record<string, unknown> }
  | { allowed: false; reason?: string; metadata?: Record<string, unknown> }

export type PolicyCallback = (evt: Event) => Promise<PolicyResult> | PolicyResult

export interface Policy {
  id: string
  description?: string
  callback: PolicyCallback
  // lower numbers run first
  priority?: number
}

class PolicyRegistry {
  private policies: Policy[] = []

  register(policy: Policy) {
    this.policies.push(policy)
    // keep policies ordered by priority
    this.policies.sort((a, b) => (a.priority ?? 100) - (b.priority ?? 100))
  }

  unregister(id: string) {
    this.policies = this.policies.filter((p) => p.id !== id)
  }

  list(): Policy[] {
    return [...this.policies]
  }

  async evaluate(evt: Event): Promise<{ allowed: boolean; decisions: Array<{ id: string; result: PolicyResult }> }> {
    const decisions: Array<{ id: string; result: PolicyResult }> = []
    for (const p of this.policies) {
      try {
        const r = await Promise.resolve(p.callback(evt))
        decisions.push({ id: p.id, result: r })
        if (!r.allowed) {
          // short-circuit on first deny
          return { allowed: false, decisions }
        }
      } catch (err) {
        // On error, treat as deny and record reason
        const r: PolicyResult = { allowed: false, reason: `policy_error: ${String(err)}` }
        decisions.push({ id: p.id, result: r })
        return { allowed: false, decisions }
      }
    }
    return { allowed: true, decisions }
  }
}

export const policyRegistry = new PolicyRegistry()

// Runtime-configurable governance knobs (modifiable via admin tooling)
const blockedWorkspaces = new Set<string>()
let maintenanceWindow: { startHour: number; endHour: number } | null = null
let toolInvocationRequireApproval = true

export function setBlockedWorkspaces(list: string[]) {
  blockedWorkspaces.clear()
  for (const w of list) blockedWorkspaces.add(w)
}

export function setMaintenanceWindow(startHour: number, endHour: number | null) {
  if (endHour === null) {
    maintenanceWindow = null
  } else {
    maintenanceWindow = { startHour, endHour }
  }
}

export function setToolInvocationRequireApproval(requireApproval: boolean) {
  toolInvocationRequireApproval = requireApproval
}

// Keep original emit so audits and system events can bypass governance checks
const originalEmit = eventBus.emit.bind(eventBus)

// Replace eventBus.emit with a guard that evaluates policies before allowing
// the event to be delivered. By default we run policies for all events except
// those emitted with { bypassGovernance: true } in meta.

// We extend the internal emit signature to optionally support bypass via meta
type EmitOpts = { persist?: boolean }

eventBus.emit = async function (evt: Event, opts: EmitOpts = { persist: true }) {
  // If caller explicitly set meta.__bypass_governance, skip checks
  if ((evt as any).meta && (evt as any).meta.__bypass_governance) {
    return originalEmit(evt, opts)
  }

  // Evaluate policies
  const evaluation = await policyRegistry.evaluate(evt)

  // Emit an audit record using the originalEmit (avoid recursing into guarded emit)
  try {
    await originalEmit(
      {
        name: 'governance.audit',
        payload: { event: evt, evaluation },
        workspace: evt.workspace,
        timestamp: new Date().toISOString(),
      },
      { persist: true }
    )
  } catch (auditErr) {
    // swallow audit failures to avoid blocking runtime; but log via a non-persistent event
    try {
      await originalEmit(
        {
          name: 'governance.audit.failed',
          payload: { error: String(auditErr), originalEvent: evt },
          workspace: evt.workspace,
          timestamp: new Date().toISOString(),
        },
        { persist: false }
      )
    } catch (_) {
      // final fallback: nothing
    }
  }

  if (!evaluation.allowed) {
    // Emit a governance.block event (non-persistent) to let local listeners react
    await originalEmit({
      name: 'governance.block',
      payload: { event: evt, decisions: evaluation.decisions },
      workspace: evt.workspace,
      timestamp: new Date().toISOString(),
    }, { persist: false })

    // Short-circuit: do not deliver the event
    return
  }

  // If allowed, deliver the event normally
  return originalEmit(evt, opts)
} as unknown as typeof eventBus.emit

// --- Production policy examples ---

// 1) Workspace block policy (reads from blockedWorkspaces set)
policyRegistry.register({
  id: 'workspace-block',
  description: 'Blocks events originating from configured blocked workspaces',
  priority: 10,
  callback: async (evt) => {
    const ws = evt.workspace || 'default'
    if (blockedWorkspaces.has(ws)) {
      return { allowed: false, reason: 'workspace_blocked', metadata: { workspace: ws } }
    }
    return { allowed: true }
  },
})

// 2) Maintenance window guard: prevents process-like events during maintenance
policyRegistry.register({
  id: 'maintenance-window-guard',
  description: 'Prevents process starts during configured maintenance window',
  priority: 20,
  callback: async (evt) => {
    if (!maintenanceWindow) return { allowed: true }
    // Only guard events that are likely to start processes
    const processCandidate = evt.name.startsWith('sim.') || evt.name.startsWith('tec.') || evt.name.startsWith('process.')
    if (!processCandidate) return { allowed: true }

    const hour = new Date().getUTCHours()
    const { startHour, endHour } = maintenanceWindow
    const inWindow = startHour <= endHour ? hour >= startHour && hour < endHour : hour >= startHour || hour < endHour
    if (inWindow) return { allowed: false, reason: 'maintenance_window', metadata: { startHour, endHour, hour } }
    return { allowed: true }
  },
})

// 3) Tool invocation guard: require explicit approval in meta for tec.tool.invoked
policyRegistry.register({
  id: 'tool-invocation-approval',
  description: 'Require explicit approval for tool invocations from untrusted sources',
  priority: 30,
  callback: async (evt) => {
    if (evt.name !== 'tec.tool.invoked') return { allowed: true }

    // If global flag disabled, allow
    if (!toolInvocationRequireApproval) return { allowed: true }

    // If event contains meta.approved === true, allow; otherwise deny
    const approved = (evt.meta && (evt.meta as any).approved) === true
    if (!approved) return { allowed: false, reason: 'tool_invocation_not_approved' }
    return { allowed: true }
  },
})

// 4) Example logging policy: low-priority annotator that always allows and adds metadata
policyRegistry.register({
  id: 'annotate-event',
  description: 'Annotates events with governance metadata for auditing',
  priority: 100,
  callback: async (evt) => {
    // This policy is intentionally side-effect-free; it returns metadata that will be
    // recorded in the governance.audit payload.
    return { allowed: true, metadata: { governedAt: new Date().toISOString() } }
  },
})

// Exported helper used by the worker entry to produce a policy context
export function applyPolicies(identity: any, body: any) {
  // Minimal policy application used for build/runtime stubbing.
  // In production, this should construct an Event-like object and run policyRegistry.evaluate(evt)
  // to produce a rich policyContext with decisions. For now return a simple context.
  return {
    allowed: true,
    decisions: policyRegistry.list().map((p) => ({ id: p.id, description: p.description }))
  }
}

// Expose API for admin tooling and configuration
export const governance = {
  policyRegistry,
  setBlockedWorkspaces,
  setMaintenanceWindow,
  setToolInvocationRequireApproval,
}

// Integration notes (how to use):
// - Import this module early in your runtime initialization so it patches eventBus.emit before components attach handlers.
//   Example in src/index.ts middleware: `import './governance/policies'` or dynamic import.
// - To bypass governance for system-internal events (audits, health checks), callers can set evt.meta.__bypass_governance = true
// - Policies should be idempotent, fast, and side-effect free where possible. Use audits for recording decisions.
