"""
Virtual Kernel v1
A lightweight kernel instance inside a hypervisor zone.
"""

class VirtualKernel:
    def __init__(self, zone):
        self.zone = zone
        self.flags = {
            "booted": False,
            "healthy": True
        }

    def boot(self):
        if not self.zone.state["initialized"]:
            return {"error": "zone_not_initialized"}
        self.flags["booted"] = True
        return {"virtual_kernel": self.zone.name, "status": "booted"}

    def health_check(self):
        if not self.flags["booted"]:
            return {"status": "error", "reason": "not_booted"}
        if not self.flags["healthy"]:
            return {"status": "error", "reason": "unhealthy"}
        return {"status": "ok"}

    def describe(self):
        return {
            "zone": self.zone.name,
            "flags": self.flags
        }
