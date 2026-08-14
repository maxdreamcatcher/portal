"""
Kernel Diagnostics v1
Provides health checks and kernel introspection.
"""

class KernelDiagnostics:
    def __init__(self, state):
        self.state = state

    def health_check(self):
        flags = self.state.flags
        if not flags["booted"]:
            return {"status": "error", "reason": "kernel_not_booted"}
        if not flags["healthy"]:
            return {"status": "error", "reason": "kernel_unhealthy"}
        return {"status": "ok"}

    def describe(self):
        return self.state.describe()
