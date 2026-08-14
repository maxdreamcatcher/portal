"""
Scheduler Policy v1
Defines scheduling rules.
"""

class SchedPolicy:
    def __init__(self, name, evaluator):
        self.name = name
        self.evaluator = evaluator

    def apply(self, queue: "SchedQueue", context):
        return self.evaluator(queue, context)

    def describe(self):
        return {"name": self.name}
