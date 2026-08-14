# Portal‑OS Kernel Signals v1

Kernel Signals provide synchronous, high-priority interrupts.

## Components

### Signal
Typed interrupt.

### SignalHandler
Synchronous handler.

### SignalRegistry
Stores handlers.

### SignalEngine
Raise + dispatch + trap.

### Example
See `kernel/signals/examples/example_signals.py`.
