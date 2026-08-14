"""
TEC Orchestration Engine v1
Portal‑OS v4

The TEC engine coordinates:
- Process orchestration
- Resource accounting
- Economics evaluation
- Pipeline execution

It acts as the runtime for TEC-level operations.
"""

class Process:
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self, context):
        return self.fn(context)


class Pipeline:
    def __init__(self, name, steps=None):
        self.name = name
        self.steps = steps or []

    def add_step(self, process: Process):
        self.steps.append(process)

    def execute(self, context):
        results = []
        for step in self.steps:
            results.append({
                "process": step.name,
                "result": step.run(context)
            })
        return results


class EconomicsModel:
    def __init__(self):
        self.metrics = {}

    def set_metric(self, name, value):
        self.metrics[name] = value

    def evaluate(self):
        return self.metrics


class TECOrchestrationEngine:
    def __init__(self):
        self.processes = {}
        self.pipelines = {}
        self.economics = EconomicsModel()

    def add_process(self, name, fn):
        process = Process(name, fn)
        self.processes[name] = process
        return process

    def add_pipeline(self, name):
        pipeline = Pipeline(name)
        self.pipelines[name] = pipeline
        return pipeline

    def attach_process_to_pipeline(self, pipeline_name, process_name):
        pipeline = self.pipelines.get(pipeline_name)
        process = self.processes.get(process_name)
        if pipeline and process:
            pipeline.add_step(process)
            return True
        return False

    def run_pipeline(self, name, context):
        pipeline = self.pipelines.get(name)
        if pipeline:
            return pipeline.execute(context)
        return None

    def set_economic_metric(self, name, value):
        self.economics.set_metric(name, value)

    def evaluate_economics(self):
        return self.economics.evaluate()

    def describe(self):
        return {
            "processes": list(self.processes.keys()),
            "pipelines": list(self.pipelines.keys()),
            "economics": self.economics.metrics
        }
