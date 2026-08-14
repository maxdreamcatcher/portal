"""
Event Bus v1
Global event registry + dispatcher.
"""

from event_bus.channel import EventChannel

class EventBus:
    def __init__(self):
        self.channels = {}

    def create_channel(self, name):
        ch = EventChannel(name)
        self.channels[name] = ch
        return ch

    def get_channel(self, name):
        return self.channels.get(name)

    def publish(self, channel, type_, payload, metadata=None):
        ch = self.get_channel(channel)
        if not ch:
            return {"error": "channel_not_found", "channel": channel}
        return ch.publish(type_, payload, metadata)

    def subscribe(self, channel, subscriber_id, handler):
        ch = self.get_channel(channel)
        if not ch:
            return {"error": "channel_not_found", "channel": channel}
        return ch.subscribe(subscriber_id, handler)

    def describe(self):
        return {name: ch.describe() for name, ch in self.channels.items()}
