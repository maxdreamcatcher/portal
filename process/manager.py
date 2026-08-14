"""
Process Manager v1
Creates, runs, suspends, resumes, and kills processes.
"""

from process.table import ProcessTable
from process.state import ProcessState

class ProcessManager:
    def __init__(self):
        self.table = ProcessTable()

    def spawn(self, domain, executor, metadata=None):
        return self.table.create(domain, executor, metadata)

    def run(self, pid, payload):
        proc = self.table.get(pid)
        if not proc:
            return {"error": "pid_not_found"}
        return proc.run(payload)

    def stop(self, pid):
        proc = self.table.get(pid)
        if not proc:
            return {"error": "pid_not_found"}
        proc.stop()
        return {"pid": pid, "status": "stopped"}

    def kill(self, pid):
        return self.table.kill(pid)

    def describe(self):
        return self.table.describe()
