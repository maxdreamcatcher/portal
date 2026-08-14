"""
TEC Pipeline v1
Defines an ordered pipeline of TEC stages.
"""

from tec.stage import TECStage

class TECPipeline:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.stages = []

    def add_stage(self, stage: TECStage):
        self.stages.append(stage)

    def run(self, ctx: "TECContext", payload):
        results = []
        current_payload = payload

        for stage in self.stages:
            result = stage.run(ctx, current_payload)
            results.append(result)
            current_payload = result["result"]

        return {
            "pipeline": self.name,
            "results": results,
            "final": current_payload
        }

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "stages": [s.describe() for s in self.stages]
        }
