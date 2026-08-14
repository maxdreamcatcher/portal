# Umbrella Lawbook v1

Umbrella Lawbook governs all Portal‑OS subsystems.

## Components

### Rules
Govern system behavior:
- Identity integrity
- Governance safety
- Routing consistency
- Substrate alignment

See `umbrella/lawbook/rules.py`.

### Invariants
Must never be violated:
- Identity must exist
- Kernel must be booted
- SIM.MODE must be loaded

See `umbrella/lawbook/invariants.py`.

### Escalation Paths
Handle violations:
- low → log
- medium → audit
- high → halt

See `umbrella/lawbook/escalation.py`.

### Engine
Coordinates rule evaluation, invariant checking, and escalation.

See `umbrella/lawbook/engine.py`.
