"""Event Simulation - World Event Propagation

Manages the creation, propagation, and cascading of events throughout the world.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import uuid
from datetime import datetime
from collections import defaultdict


class EventType(Enum):
    """Types of events."""
    ENTITY_CREATED = "entity_created"
    ENTITY_DESTROYED = "entity_destroyed"
    STATE_CHANGED = "state_changed"
    COLLISION = "collision"
    FORCE_APPLIED = "force_applied"
    BEHAVIOR_EXECUTED = "behavior_executed"
    CUSTOM = "custom"


class EventPriority(Enum):
    """Priority of events."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class SimulationEvent:
    """An event in the world simulation."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_entity: str = ""
    affected_entities: List[str] = field(default_factory=list)
    priority: EventPriority = EventPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    cascade: bool = False  # Should this event cascade to children?
    parent_event: Optional[str] = None
    child_events: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventSimulator:
    """Simulates event propagation in the world."""

    def __init__(self):
        self.event_log: List[SimulationEvent] = []
        self.event_queue: List[SimulationEvent] = []
        self.event_subscriptions: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: Dict[str, SimulationEvent] = {}
        self.cascade_depth = 0
        self.max_cascade_depth = 10

    def create_event(
        self,
        event_type: EventType,
        source_entity: str,
        affected_entities: List[str] = None,
        payload: Dict[str, Any] = None,
        priority: EventPriority = EventPriority.NORMAL,
        cascade: bool = False,
    ) -> str:
        """Create a new event."""
        event = SimulationEvent(
            event_type=event_type,
            source_entity=source_entity,
            affected_entities=affected_entities or [],
            payload=payload or {},
            priority=priority,
            cascade=cascade,
        )
        self.event_queue.append(event)
        self.event_history[event.event_id] = event
        return event.event_id

    def subscribe(
        self,
        event_type: EventType,
        callback: Callable,
    ) -> str:
        """Subscribe to an event type."""
        self.event_subscriptions[event_type].append(callback)
        return str(uuid.uuid4())

    def process_events(self) -> int:
        """Process all queued events."""
        events_processed = 0

        # Sort by priority
        self.event_queue.sort(key=lambda e: e.priority.value)

        while self.event_queue:
            event = self.event_queue.pop(0)
            self._dispatch_event(event)
            self.event_log.append(event)
            events_processed += 1

        return events_processed

    def _dispatch_event(self, event: SimulationEvent) -> None:
        """Dispatch an event to subscribers."""
        callbacks = self.event_subscriptions.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")

        # Handle cascading
        if event.cascade and self.cascade_depth < self.max_cascade_depth:
            self.cascade_depth += 1
            # Create cascade events for affected entities
            for entity_id in event.affected_entities:
                cascade_event = SimulationEvent(
                    event_type=event.event_type,
                    source_entity=entity_id,
                    affected_entities=event.affected_entities,
                    priority=EventPriority(event.priority.value + 1),  # Lower priority
                    parent_event=event.event_id,
                )
                event.child_events.append(cascade_event.event_id)
                self.event_queue.append(cascade_event)
            self.cascade_depth -= 1

    def get_event_causal_chain(self, event_id: str) -> List[SimulationEvent]:
        """Get the causal chain of an event."""
        chain = []
        current_id = event_id

        while current_id:
            event = self.event_history.get(current_id)
            if not event:
                break
            chain.insert(0, event)
            current_id = event.parent_event

        return chain

    def get_event_cascade_tree(self, event_id: str) -> Dict[str, Any]:
        """Get the cascade tree of an event."""
        event = self.event_history.get(event_id)
        if not event:
            return {}

        return {
            'event_id': event_id,
            'type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'child_events': [
                self.get_event_cascade_tree(child_id)
                for child_id in event.child_events
            ],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics."""
        return {
            'total_events': len(self.event_log),
            'queued_events': len(self.event_queue),
            'event_types': {
                et.value: len([e for e in self.event_log if e.event_type == et])
                for et in EventType
            },
        }
