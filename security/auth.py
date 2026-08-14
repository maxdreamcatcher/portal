"""
Security Auth v1
Provides authentication and authorization helpers.
"""

from security.context import SecurityContext

class SecurityAuth:
    def __init__(self, policy_engine):
        self.policy_engine = policy_engine

    def authenticate(self, identity, metadata=None):
        ctx = SecurityContext(identity, metadata)
        ctx.set_flag("authenticated", True)
        return ctx

    def authorize(self, ctx: SecurityContext, permission_name):
        allowed = self.policy_engine.is_allowed(ctx.identity, permission_name)
        ctx.set_flag("authorized", allowed)
        return {
            "permission": permission_name,
            "allowed": allowed,
            "context": ctx.describe()
        }
