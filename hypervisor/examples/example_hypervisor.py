"""
Example Hypervisor v1
Demonstrates zone creation, virtual kernel boot, and sandbox execution.
"""

from hypervisor.manager import HypervisorManager

def build_example_hypervisor():
    hv = HypervisorManager()

    # Create zone
    zone = hv.create_zone("sim_zone", {"memory": "256MB", "cpu": "1vCPU"})
    zone.initialize()
    zone.start()

    # Boot virtual kernel
    vk = hv.boot_kernel("sim_zone")

    # Create sandbox
    sb = hv.create_sandbox("sim_zone")

    # Execute tasks
    result1 = sb.execute("sim_task", lambda ctx: {"sim": "executed"})
    result2 = sb.execute("tec_task", lambda ctx: {"tec": "executed"})

    return hv, {
        "zone": zone.describe(),
        "kernel": vk.describe(),
        "sandbox": sb.describe(),
        "results": [result1, result2]
    }
