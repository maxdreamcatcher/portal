"""
Kernel Scheduler Engine v1
Coordinates tasks, queues, and policies.
"""

from kernel.scheduler.queue import SchedQueue
from kernel.scheduler.task import SchedTask
from kernel.scheduler.policy import SchedPolicy

class KernelScheduler:
    def __init__(self):
        self.queue = SchedQueue()
        self.policies = {}

    def add_task(self, name, priority, executor):
        task = SchedTask(name, priority, executor)
        self.queue.add(task)
        return task

    def add_policy(self, name, evaluator):
        policy = SchedPolicy(name, evaluator)
        self.policies[name] = policy
        return policy

    def run_once(self, context):
        # Apply policies
        for policy in self.policies.values():
            policy.apply(self.queue, context)

        # Pop next task
        task = self.queue.pop()
        if not task:
            return {"status": "idle"}

        return task.run(context)

    def run(self, context, ticks=1):
        results = []
        for _ in range(ticks):
            results.append(self.run_once(context))
        return results

    def describe(self):
        return {
            "queue": self.queue.describe(),
            "policies": list(self.policies.keys())
        }
