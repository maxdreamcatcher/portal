"""
Process Table v1
Global registry of all processes.
"""

from process.process import Process

class ProcessTable:
    def __init__(self):
        self.processes = {}
        self.next_pid = 1

    def create(self, domain, executor, metadata=None):
        pid = self.next_pid
        self.next_pid += 1

        proc = Process(pid, domain, executor, metadata)
        proc.set_state("ready")
        self.processes[pid] = proc
        return proc

    def get(self, pid):
        return self.processes.get(pid)

    def kill(self, pid):
        proc = self.get(pid)
        if not proc:
            return {"error": "pid_not_found"}
        proc.kill()
        return {"pid": pid, "status": "killed"}

    def describe(self):
        return {pid: p.describe() for pid, p in self.processes.items()}
