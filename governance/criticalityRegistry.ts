// governance/criticalityRegistry.ts
// Central registry for process-type -> criticality mapping

import type { ProcessCriticality } from '../core/processManager'

type Mapping = { [typePattern: string]: ProcessCriticality }

// Canonical mapping (order matters: exact keys first, then wildcard patterns)
const canonical: Mapping = {
  // Critical
  'sim.boot': 'critical',
  'sim.identity.loaded': 'critical',
  'sim.context.initialized': 'critical',
  'sim.governance.changed': 'critical',
  'sim.identity.physics.': 'critical', // prefix match
  'substrate.ingest': 'critical',
  'substrate.publisher': 'critical',
  'substrate.audit': 'critical',
  'governance.audit': 'critical',
  'governance.config.updated': 'critical',
  'governance.reactive': 'critical',
  'routing.core': 'critical',
  'routing.governance-pressure': 'critical',
  'admin.config': 'critical',
  'admin.audit': 'critical',

  // Medium
  'identity-sync': 'medium',
  'context-sync': 'medium',

  // Non-critical
  'tec.tool.invoked': 'non-critical',
  'tec.tool.pipeline': 'non-critical',
  'workspace.cache': 'non-critical',
  'workspace.analytics': 'non-critical',
  'workspace.metrics': 'non-critical',
  'ephemeral': 'non-critical',
}

// Overrides registered at runtime
const overrides: Map<string, ProcessCriticality> = new Map()

export function getCriticalityForType(type: string): ProcessCriticality {
  // exact override
  if (overrides.has(type)) return overrides.get(type) as ProcessCriticality

  // exact key
  if (canonical[type]) return canonical[type]

  // prefix matches (e.g., sim.identity.physics.)
  for (const k of Object.keys(canonical)) {
    if (k.endsWith('.') && type.startsWith(k)) return canonical[k]
  }

  // fallback default
  return 'non-critical'
}

export function registerOverride(type: string, crit: ProcessCriticality) {
  overrides.set(type, crit)
}

export function listMappings(): { canonical: Mapping; overrides: Array<[string, ProcessCriticality]> } {
  return { canonical, overrides: Array.from(overrides.entries()) }
}
