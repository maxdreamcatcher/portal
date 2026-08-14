"""
Security Context v1
Holds per-request security state.
"""

class SecurityContext:
    def __init__(self, identity: "SecurityIdentity", metadata=None):
        self.identity = identity
        self.metadata = metadata or {}
        self.flags = {
            "authenticated": False,
            "authorized": False
        }

    def set_flag(self, key, value):
        self.flags[key] = value

    def get_flag(self, key):
        return self.flags.get(key)

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key, default=None):
        return self.metadata.get(key, default)

    def describe(self):
        return {
            "identity": self.identity.describe(),
            "metadata": self.metadata,
            "flags": self.flags
        }
