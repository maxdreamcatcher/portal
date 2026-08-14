"""
Security Permission v1
Defines a capability unit.
"""

class SecurityPermission:
    def __init__(self, name, description="", roles=None):
        self.name = name
        self.description = description
        self.roles = roles or []

    def is_allowed_for(self, identity: "SecurityIdentity"):
        if not self.roles:
            return True
        return any(identity.has_role(r) for r in self.roles)

    def describe(self):
        return {
            "name": self.name,
            "description": self.description,
            "roles": self.roles
        }
