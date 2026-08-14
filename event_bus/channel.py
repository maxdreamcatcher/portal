"""
Event Channel v1
Pub/sub channel for broadcast events.
"""

from event_bus.event import Event
from event_bus.subscription import EventSubscription

class EventChannel:
    def __init__(self, name):
        self.name = name
        self.subscribers = []

    def publish(self, type_, payload, metadata=None):
        event = Event(self.name, type_, payload, metadata)
        results = []
        for sub in self.subscribers:
            results.append(sub.notify(event))
        return {
            "event": event.describe(),
            "results": results
        }

    def subscribe(self, subscriber_id, handler):
        sub = EventSubscription(subscriber_id, handler)
        self.subscribers.append(sub)
        return sub

    def describe(self):
        return {
            "name": self.name,
            "subscribers": [s.describe() for s in self.subscribers]
        }
