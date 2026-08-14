export function applyOverrides(identity: any, body: any) {
  // Minimal build-time stub.
  // Replace with real governance override logic later.
  return {
    overridesApplied: false,
    identity: identity?.subject || 'anonymous'
  }
}
