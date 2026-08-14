# TEC Orchestration Engine v1

TEC orchestrates:
- Processes
- Pipelines
- Economics
- Resource accounting

## Architecture

### Process
A function with a name and execution context.

### Pipeline
A sequence of processes executed deterministically.

### Economics Model
Tracks TEC metrics.

### TECOrchestrationEngine
Coordinates all TEC operations.

See:
- `tec/orchestration/engine.py`
- `tec/processes/example_process.py`
- `tec/pipelines/example_pipeline.py`
