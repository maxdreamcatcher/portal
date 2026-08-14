"""
Process State v1
Defines lifecycle states for a process.
"""

class ProcessState:
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    STOPPED = "stopped"
    DEAD = "dead"
