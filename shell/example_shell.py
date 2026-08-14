"""
Example Portal‑OS Shell v1
Demonstrates CLI + API usage.
"""

from shell.cli.shell import PortalShell
from shell.api.server import ApiServer

def build_example_shell():
    shell = PortalShell()
    api = ApiServer()

    # CLI commands
    shell.register_command("ping", "Ping the system.", lambda args: {"status": "pong"})
    shell.register_command("echo", "Echo input.", lambda args: {"echo": " ".join(args)})

    # API routes
    api.add_route("/ping", lambda payload: {"status": "pong"})
    api.add_route("/echo", lambda payload: {"echo": payload.get("text", "")})

    return shell, api
