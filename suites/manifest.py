"""
Suite Manifest v1
Defines metadata and capabilities for a Portal‑OS suite.
"""

class SuiteManifest:
    def __init__(self, name, version, description, capabilities=None):
        self.name = name
        self.version = version
        self.description = description
        self.capabilities = capabilities or []

    def describe(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities
        }
