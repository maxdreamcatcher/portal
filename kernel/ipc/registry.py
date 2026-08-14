"""
IPC Registry v1
Registry of all IPC channels.
"""

from kernel.ipc.channel import IPCChannel

class IPCRegistry:
    def __init__(self):
        self.channels = {}

    def create_channel(self, name):
        ch = IPCChannel(name)
        self.channels[name] = ch
        return ch

    def get_channel(self, name):
        return self.channels.get(name)

    def describe(self):
        return {name: ch.describe() for name, ch in self.channels.items()}
