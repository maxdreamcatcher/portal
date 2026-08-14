"""
Governance Console v1
Provides CLI-level governance controls for Portal‑OS.
"""

class GovernanceConsole:
    def __init__(self, lawbook_engine):
        self.lawbook = lawbook_engine
        self.commands = {}

    def register(self, name, handler, description=""):
        self.commands[name] = {
            "handler": handler,
            "description": description
        }

    def execute(self, name, args):
        cmd = self.commands.get(name)
        if not cmd:
            return {"error": "governance_command_not_found"}
        return cmd["handler"](args)

    def describe(self):
        return {name: cmd["description"] for name, cmd in self.commands.items()}
