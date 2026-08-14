"""
Hypervisor Sandbox v1
Provides isolated execution for tasks or suites.
"""

class HypervisorSandbox:
    def __init__(self, zone):
        self.zone = zone
        self.logs = []

    def execute(self, name, executor, context=None):
        if not self.zone.state["running"]:
            return {"error": "zone_not_running"}

        ctx = context or {}
        result = executor(ctx)
        self.logs.append({"task": name, "result": result})
        return {"sandbox": self.zone.name, "task": name, "result": result}

    def describe(self):
        return {
            "zone": self.zone.name,
            "logs": self.logs
        }
