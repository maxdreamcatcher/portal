"""
Scheduler Queue v1
Priority-based task queue.
"""

class SchedQueue:
    def __init__(self):
        self.tasks = []

    def add(self, task: "SchedTask"):
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def pop(self):
        if not self.tasks:
            return None
        return self.tasks.pop(0)

    def describe(self):
        return [task.describe() for task in self.tasks]
