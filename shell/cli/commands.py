"""
Portal‑OS Shell Commands v1
Defines CLI commands and their handlers.
"""

class ShellCommand:
    def __init__(self, name, description, handler):
        self.name = name
        self.description = description
        self.handler = handler

    def run(self, args):
        return self.handler(args)


class CommandRegistry:
    def __init__(self):
        self.commands = {}

    def register(self, name, description, handler):
        cmd = ShellCommand(name, description, handler)
        self.commands[name] = cmd
        return cmd

    def run(self, name, args):
        cmd = self.commands.get(name)
        if not cmd:
            return {"error": "command_not_found"}
        return cmd.run(args)

    def describe(self):
        return {name: cmd.description for name, cmd in self.commands.items()}
