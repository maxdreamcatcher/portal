"""
Security Policy Engine v1
Evaluates security policies and permissions.
"""

from security.permission import SecurityPermission

class SecurityPolicyEngine:
    def __init__(self):
        self.permissions = {}

    def register_permission(self, name, description="", roles=None):
        perm = SecurityPermission(name, description, roles)
        self.permissions[name] = perm
        return perm

    def is_allowed(self, identity, permission_name):
        perm = self.permissions.get(permission_name)
        if not perm:
            return False
        return perm.is_allowed_for(identity)

    def describe(self):
        return {name: perm.describe() for name, perm in self.permissions.items()}
