"""
Event Subscription v1
Represents a subscriber to an event channel.
"""

class EventSubscription:
    def __init__(self, subscriber_id, handler):
        self.subscriber_id = subscriber_id
        self.handler = handler

    def notify(self, event):
        return self.handler(event)

    def describe(self):
        return {
            "subscriber": self.subscriber_id
        }
