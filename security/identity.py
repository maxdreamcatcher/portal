"""
Security Identity v1
Defines a security principal in Portal‑OS.
"""

class SecurityIdentity:
    def __init__(self, id_, roles=None, attributes=None):
        self.id = id_
        self.roles = roles or []
        self.attributes = attributes or {}

    def has_role(self, role):
        return role in self.roles

    def get_attribute(self, key, default=None):
        return self.attributes.get(key, default)

    def describe(self):
        return {
            "id": self.id,
            "roles": self.roles,
            "attributes": self.attributes
        }
