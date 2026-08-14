"""
Process v1
Atomic execution unit in Portal‑OS.
"""

from process.state import ProcessState

class Process:
    def __init__(self, pid, domain, executor, metadata=None):
        self.pid = pid
        self.domain = domain
        self.executor = executor
        self.metadata = metadata or {}
        self.state = ProcessState.NEW
        self.context = {}
        self.history = []

    def set_state(self, new_state):
        self.state = new_state
        self.history.append({"state": new_state})

    def run(self, payload):
        if self.state in [ProcessState.DEAD, ProcessState.STOPPED]:
            return {"error": "process_not_runnable", "pid": self.pid}

        self.set_state(ProcessState.RUNNING)
        result = self.executor(self, payload)
        self.history.append({"result": result})
        self.set_state(ProcessState.READY)
        return result

    def stop(self):
        self.set_state(ProcessState.STOPPED)

    def kill(self):
        self.set_state(ProcessState.DEAD)

    def describe(self):
        return {
            "pid": self.pid,
            "domain": self.domain,
            "state": self.state,
            "metadata": self.metadata,
            "history": self.history
        }
