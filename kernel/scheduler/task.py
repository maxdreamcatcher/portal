"""
Scheduler Task v1
Defines a schedulable unit of work.
"""

class SchedTask:
    def __init__(self, name, priority, executor):
        self.name = name
        self.priority = priority
        self.executor = executor
        self.completed = False

    def run(self, context):
        result = self.executor(context)
        self.completed = True
        return {
            "task": self.name,
            "priority": self.priority,
            "result": result
        }

    def describe(self):
        return {
            "name": self.name,
            "priority": self.priority,
            "completed": self.completed
        }
