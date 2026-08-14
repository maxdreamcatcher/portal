"""
Driver Manifest v1
Defines metadata for a kernel driver.
"""

class DriverManifest:
    def __init__(self, name, version, description, provides=None):
        self.name = name
        self.version = version
        self.description = description
        self.provides = provides or []

    def describe(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "provides": self.provides
        }
