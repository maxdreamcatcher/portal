"""
Portal‑OS Shell v1
Coordinates parser + command registry.
"""

from shell.cli.parser import ShellParser
from shell.cli.commands import CommandRegistry

class PortalShell:
    def __init__(self):
        self.parser = ShellParser()
        self.registry = CommandRegistry()

    def register_command(self, name, description, handler):
        return self.registry.register(name, description, handler)

    def execute(self, raw):
        command, args = self.parser.parse(raw)
        if not command:
            return {"error": "empty_input"}
        return self.registry.run(command, args)

    def describe(self):
        return self.registry.describe()
