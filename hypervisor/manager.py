"""
Hypervisor Manager v1
Coordinates zones, virtual kernels, and sandboxes.
"""

from hypervisor.zone import HypervisorZone
from hypervisor.virtual_kernel import VirtualKernel
from hypervisor.sandbox import HypervisorSandbox

class HypervisorManager:
    def __init__(self):
        self.zones = {}
        self.kernels = {}
        self.sandboxes = {}

    def create_zone(self, name, config=None):
        zone = HypervisorZone(name, config)
        self.zones[name] = zone
        return zone

    def boot_kernel(self, zone_name):
        zone = self.zones.get(zone_name)
        if not zone:
            return {"error": "zone_not_found"}

        kernel = VirtualKernel(zone)
        self.kernels[zone_name] = kernel
        zone.initialize()
        kernel.boot()
        return kernel

    def create_sandbox(self, zone_name):
        zone = self.zones.get(zone_name)
        if not zone:
            return {"error": "zone_not_found"}

        sandbox = HypervisorSandbox(zone)
        self.sandboxes[zone_name] = sandbox
        return sandbox

    def describe(self):
        return {
            "zones": {name: z.describe() for name, z in self.zones.items()},
            "kernels": {name: k.describe() for name, k in self.kernels.items()},
            "sandboxes": {name: s.describe() for name, s in self.sandboxes.items()}
        }
