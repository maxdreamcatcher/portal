"""
Driver Registry v1
Stores and manages kernel drivers.
"""

class DriverRegistry:
    def __init__(self):
        self.drivers = {}

    def register(self, driver: "KernelDriver"):
        self.drivers[driver.manifest.name] = driver

    def load(self, name, context):
        driver = self.drivers.get(name)
        if not driver:
            return {"error": "driver_not_found"}
        return driver.load(context)

    def describe(self):
        return {name: driver.describe() for name, driver in self.drivers.items()}
