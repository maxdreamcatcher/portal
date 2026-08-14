"""
Suite Engine v1
Coordinates suite registration and loading.
"""

from suites.registry import SuiteRegistry
from suites.suite import Suite
from suites.manifest import SuiteManifest

class SuiteEngine:
    def __init__(self):
        self.registry = SuiteRegistry()

    def create_suite(self, name, version, description, capabilities, initializer=None):
        manifest = SuiteManifest(name, version, description, capabilities)
        suite = Suite(manifest, initializer)
        self.registry.register(suite)
        return suite

    def load_suite(self, name, context):
        return self.registry.load(name, context)

    def describe(self):
        return self.registry.describe()
