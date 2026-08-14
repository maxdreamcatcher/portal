"""
Kernel Driver v1
Represents a loaded driver.
"""

class KernelDriver:
    def __init__(self, manifest, initializer=None):
        self.manifest = manifest
        self.initializer = initializer
        self.loaded = False

    def load(self, context):
        if self.initializer:
            self.initializer(context)
        self.loaded = True
        return {"status": "driver_loaded", "driver": self.manifest.name}

    def describe(self):
        return {
            "manifest": self.manifest.describe(),
            "loaded": self.loaded
        }
