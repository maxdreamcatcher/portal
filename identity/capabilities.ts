export function applyCapabilities(identity: any) {
  // Minimal build-time stub.
  // Replace with full capability derivation later.
  return {
    roles: [],
    canCompute: true,
    source: identity?.subject || 'anonymous'
  }
}
