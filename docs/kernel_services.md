# Portal‑OS Kernel Services v1

Kernel Services provide:
- Global kernel state
- Event dispatch
- Message routing
- Diagnostics
- Boot primitives

## Components

### KernelState
Tracks kernel flags and metadata.

### KernelEventBus
Dispatches system events.

### KernelBus
Routes messages between kernel subsystems.

### KernelDiagnostics
Provides health checks.

### KernelServicesEngine
Coordinates all kernel services.
