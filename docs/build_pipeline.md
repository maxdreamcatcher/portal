# Portal‑OS Build Pipeline v1

The build pipeline orchestrates the construction of Portal‑OS.

## Components

### BuildStep
Atomic build unit.

### BuildPhase
Ordered group of steps.

### BuildPipeline
Coordinates phases.

### BuildEngine
Top-level build coordinator.

### Example Pipeline
Kernel → Routing → Substrate → Umbrella → Suites

