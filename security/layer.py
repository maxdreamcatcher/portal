"""
Security Layer v1
Top-level security façade for Portal‑OS.
"""

from security.policy_engine import SecurityPolicyEngine
from security.auth import SecurityAuth

class SecurityLayer:
    def __init__(self):
        self.policy_engine = SecurityPolicyEngine()
        self.auth = SecurityAuth(self.policy_engine)

    def register_permission(self, name, description="", roles=None):
        return self.policy_engine.register_permission(name, description, roles)

    def authenticate(self, identity, metadata=None):
        return self.auth.authenticate(identity, metadata)

    def authorize(self, ctx, permission_name):
        return self.auth.authorize(ctx, permission_name)

    def describe(self):
        return {
            "permissions": self.policy_engine.describe()
        }
