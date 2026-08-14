"""
Governance Console Builder v1
Registers all governance commands.
"""

from governance.console.console import GovernanceConsole
from governance.console.commands import (
    cmd_rules,
    cmd_invariants,
    cmd_escalate,
    cmd_describe
)

def build_governance_console(lawbook_engine):
    console = GovernanceConsole(lawbook_engine)

    console.register(
        "rules",
        lambda args: cmd_rules(console, args),
        "Evaluate Umbrella rules."
    )

    console.register(
        "invariants",
        lambda args: cmd_invariants(console, args),
        "Check Umbrella invariants."
    )

    console.register(
        "escalate",
        lambda args: cmd_escalate(console, args),
        "Trigger an escalation path."
    )

    console.register(
        "describe",
        lambda args: cmd_describe(console, args),
        "Describe the lawbook."
    )

    return console
