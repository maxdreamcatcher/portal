"""
Signal Engine v1
Raise + dispatch + trap synchronous kernel signals.
"""

from kernel.signals.signal import Signal
from kernel.signals.registry import SignalRegistry
from kernel.signals.handler import SignalHandler

class SignalEngine:
    def __init__(self):
        self.registry = SignalRegistry()
        self.trap_log = []

    def register_handler(self, signal_name, description, executor):
        handler = SignalHandler(signal_name, description, executor)
        self.registry.register(signal_name, handler)
        return handler

    def raise_signal(self, name, severity, payload=None, metadata=None):
        signal = Signal(name, severity, payload, metadata)
        handler = self.registry.get(name)

        if not handler:
            self.trap_log.append({
                "signal": signal.describe(),
                "error": "no_handler"
            })
            return {"error": "no_handler", "signal": signal.describe()}

        result = handler.run(signal)
        self.trap_log.append({
            "signal": signal.describe(),
            "result": result
        })
        return result

    def describe(self):
        return {
            "registry": self.registry.describe(),
            "trap_log": self.trap_log
        }
