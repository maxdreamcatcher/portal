"""
Portal‑OS Scheduler v1
Multi-domain scheduler used by the kernel runtime.

Responsibilities:
- Manage domain queues
- Apply scheduling policies
- Dispatch tasks
"""

class Scheduler:
    def __init__(self):
        self.queues = {}
        self.policies = ["fair-share", "domain-priority"]

    def add_queue(self, name):
        self.queues[name] = []
        return True

    def schedule(self, domain, task):
        if domain not in self.queues:
            self.add_queue(domain)
        self.queues[domain].append(task)
        return True

    def next_task(self, domain):
        if domain in self.queues and self.queues[domain]:
            return self.queues[domain].pop(0)
        return None
