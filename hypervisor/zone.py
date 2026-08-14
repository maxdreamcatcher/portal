"""
Hypervisor Zone v1
Defines an isolated execution zone.
"""

class HypervisorZone:
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.state = {
            "initialized": False,
            "running": False,
            "terminated": False
        }

    def initialize(self):
        self.state["initialized"] = True
        return {"zone": self.name, "status": "initialized"}

    def start(self):
        if not self.state["initialized"]:
            return {"error": "zone_not_initialized"}
        self.state["running"] = True
        return {"zone": self.name, "status": "running"}

    def terminate(self):
        self.state["terminated"] = True
        self.state["running"] = False
        return {"zone": self.name, "status": "terminated"}

    def describe(self):
        return {
            "name": self.name,
            "config": self.config,
            "state": self.state
        }
