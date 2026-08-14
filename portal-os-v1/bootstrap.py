from kernel.scheduler import Scheduler
from runtime.engine import RuntimeEngine
from hypervisor.hypervisor import Hypervisor
from substrate.engine import SubstrateEngine
from cognitive.engine import CognitiveEngine
from tec.engine import TECEngine
from sim.engine import SimEngine
from umbrella.engine import UmbrellaEngine
from domain_router.router import DomainRouter
from suites.engine import SuiteEngine
from ipc.bus import IPCBus
from event_bus.bus import EventBus
from memory.manager import MemoryManager
from signals.engine import SignalEngine
from process.manager import ProcessManager
from fs.filesystem import FileSystem
from network.stack import NetworkStack

def build_portal_os_v1():
    scheduler = Scheduler()
    runtime = RuntimeEngine()
    hypervisor = Hypervisor()
    substrate = SubstrateEngine()
    cognitive = CognitiveEngine()
    tec = TECEngine()
    sim = SimEngine()
    umbrella = UmbrellaEngine()
    domain = DomainRouter()
    suites = SuiteEngine()
    ipc = IPCBus()
    events = EventBus()
    memory = MemoryManager()
    signals = SignalEngine()
    processes = ProcessManager()
    fs = FileSystem()
    net = NetworkStack()

    # minimal wiring example
    fs.mount("runtime")
    net.create_interface("runtime")
    net.create_channel("core")
    net.attach("core", "runtime")
    net.add_route("runtime", "core")

    return {
        "scheduler": scheduler,
        "runtime": runtime,
        "hypervisor": hypervisor,
        "substrate": substrate,
        "cognitive": cognitive,
        "tec": tec,
        "sim": sim,
        "umbrella": umbrella,
        "domain": domain,
        "suites": suites,
        "ipc": ipc,
        "events": events,
        "memory": memory,
        "signals": signals,
        "processes": processes,
        "fs": fs,
        "net": net,
    }

if __name__ == "__main__":
    os = build_portal_os_v1()
    print("Portal‑OS v1 booted.")
