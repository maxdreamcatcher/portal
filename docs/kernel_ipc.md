# Portal‑OS Kernel IPC v1

Kernel IPC provides message-based communication across Portal‑OS subsystems.

## Components

### IPCMessage
Typed message object.

### IPCChannel
FIFO message queue.

### IPCRegistry
Registry of channels.

### IPCEngine
Send/receive/dispatch messages.

### Example
See `kernel/ipc/examples/example_ipc.py`.
