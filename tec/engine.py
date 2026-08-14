"""
TEC Engine v1
Registry + executor for TEC pipelines.
"""

from tec.pipeline import TECPipeline
from tec.context import TECContext

class TECEngine:
    def __init__(self):
        self.pipelines = {}

    def register_pipeline(self, pipeline: TECPipeline):
        self.pipelines[pipeline.name] = pipeline

    def get_pipeline(self, name):
        return self.pipelines.get(name)

    def run(self, pipeline_name, payload, metadata=None):
        pipeline = self.get_pipeline(pipeline_name)
        if not pipeline:
            return {"error": "pipeline_not_found"}

        ctx = TECContext(metadata)
        return pipeline.run(ctx, payload)

    def describe(self):
        return {name: p.describe() for name, p in self.pipelines.items()}
