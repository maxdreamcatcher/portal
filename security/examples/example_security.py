"""
Example Security Layer v1
Demonstrates identity, permissions, and authorization.
"""

from security.identity import SecurityIdentity
from security.layer import SecurityLayer

def build_example_security():
    sec = SecurityLayer()

    # Register permissions
    sec.register_permission(
        "governance.read",
        "Read Umbrella governance state.",
        roles=["governance", "admin"]
    )
    sec.register_permission(
        "governance.write",
        "Modify Umbrella governance state.",
        roles=["admin"]
    )
    sec.register_permission(
        "runtime.execute",
        "Execute runtime operations.",
        roles=["runtime", "admin"]
    )

    # Build identity
    identity = SecurityIdentity(
        id_="user:max",
        roles=["runtime"],
        attributes={"display_name": "Max"}
    )

    # Authenticate
    ctx = sec.authenticate(identity, metadata={"session": "abc123"})

    # Authorize
    result_read = sec.authorize(ctx, "governance.read")
    result_exec = sec.authorize(ctx, "runtime.execute")

    return sec, ctx, {
        "governance_read": result_read,
        "runtime_execute": result_exec
    }
