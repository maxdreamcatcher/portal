"""
Driver Engine v1
Coordinates driver registration and loading.
"""

from kernel.drivers.registry import DriverRegistry
from kernel.drivers.driver import KernelDriver
from kernel.drivers.manifest import DriverManifest

class DriverEngine:
    def __init__(self):
        self.registry = DriverRegistry()

    def create_driver(self, name, version, description, provides, initializer=None):
        manifest = DriverManifest(name, version, description, provides)
        driver = KernelDriver(manifest, initializer)
        self.registry.register(driver)
        return driver

    def load_driver(self, name, context):
        return self.registry.load(name, context)

    def describe(self):
        return self.registry.describe()
