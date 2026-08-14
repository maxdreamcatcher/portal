"""World Kernel Lattice - Hierarchical State Structure

Implements a hierarchical lattice for maintaining global state with
causality preservation and multi-domain consistency.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid
from datetime import datetime
from collections import defaultdict


class EventType(Enum):
    """Types of events in the lattice."""
    STATE_UPDATE = "state_update"
    STATE_COMMIT = "state_commit"
    CONSENSUS_PROPOSAL = "consensus_proposal"
    CONSENSUS_VOTE = "consensus_vote"
    DOMAIN_SYNC = "domain_sync"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class VectorClock:
    """Vector clock for causality tracking across domains."""
    clock: Dict[str, int] = field(default_factory=dict)

    def increment(self, domain_id: str):
        """Increment clock for a domain."""
        self.clock[domain_id] = self.clock.get(domain_id, 0) + 1

    def update(self, other: 'VectorClock'):
        """Update this clock with another (causality merge)."""
        for domain_id, timestamp in other.clock.items():
            self.clock[domain_id] = max(self.clock.get(domain_id, 0), timestamp)

    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this event happens before another."""
        strictly_less = False
        for domain_id in set(self.clock.keys()) | set(other.clock.keys()):
            t1 = self.clock.get(domain_id, 0)
            t2 = other.clock.get(domain_id, 0)
            if t1 > t2:
                return False
            if t1 < t2:
                strictly_less = True
        return strictly_less

    def concurrent_with(self, other: 'VectorClock') -> bool:
        """Check if two events are concurrent."""
        return not self.happens_before(other) and not other.happens_before(self)

    def __repr__(self) -> str:
        return f"VC{self.clock}"


@dataclass
class LatticeEvent:
    """An event in the world kernel lattice."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.STATE_UPDATE
    domain_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    vector_clock: VectorClock = field(default_factory=VectorClock)
    state_key: str = ""  # path in global state
    state_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_events: List[str] = field(default_factory=list)  # causality

    def __lt__(self, other: 'LatticeEvent') -> bool:
        """Compare events by causality."""
        return self.vector_clock.happens_before(other.vector_clock)


class LatticeLevel:
    """A level in the hierarchical lattice."""

    def __init__(
        self,
        level: int,
        name: str,
        domains: Set[str],
    ):
        self.level = level
        self.name = name
        self.domains = domains
        self.state: Dict[str, Any] = {}
        self.events: List[LatticeEvent] = []
        self.committed_events: Set[str] = set()
        self.pending_events: Dict[str, LatticeEvent] = {}

    def add_event(self, event: LatticeEvent) -> bool:
        """Add an event to this level."""
        if event.domain_id not in self.domains:
            return False

        self.events.append(event)
        self.pending_events[event.event_id] = event
        return True

    def commit_event(self, event_id: str) -> bool:
        """Commit an event at this level."""
        if event_id not in self.pending_events:
            return False

        event = self.pending_events[event_id]
        self.state[event.state_key] = event.state_value
        self.committed_events.add(event_id)
        del self.pending_events[event_id]
        return True

    def get_state(self, key: str) -> Any:
        """Get state value at this level."""
        return self.state.get(key)

    def get_pending_events(self) -> List[LatticeEvent]:
        """Get all pending events at this level."""
        return list(self.pending_events.values())


class WorldKernelLattice:
    """Hierarchical lattice maintaining global state consistency.

    Structure:
    Level 0 (World): Single world domain - global consensus
    Level 1 (Regions): Regional coordinators - regional consensus
    Level 2 (Zones): Local clusters - zone consensus
    Level 3 (Entities): Individual domains - local state
    """

    def __init__(self):
        self.levels: Dict[int, LatticeLevel] = {}
        self.world_domain_id: Optional[str] = None
        self.event_log: List[LatticeEvent] = []
        self.causality_graph: Dict[str, List[str]] = defaultdict(list)
        self.vector_clocks: Dict[str, VectorClock] = defaultdict(VectorClock)

    def create_level(
        self,
        level: int,
        name: str,
        domains: Set[str],
    ) -> bool:
        """Create a new level in the lattice."""
        if level in self.levels:
            return False

        self.levels[level] = LatticeLevel(level, name, domains)
        return True

    def submit_event(self, event: LatticeEvent) -> bool:
        """Submit an event to the lattice."""
        # Update vector clock
        self.vector_clocks[event.domain_id].increment(event.domain_id)
        event.vector_clock = self.vector_clocks[event.domain_id]

        # Add to event log
        self.event_log.append(event)

        # Determine which level this event belongs to
        target_level = self._determine_level(event.domain_id)
        if target_level not in self.levels:
            return False

        # Add to appropriate level
        return self.levels[target_level].add_event(event)

    def commit_event(
        self,
        event_id: str,
        level: int,
    ) -> bool:
        """Commit an event at a specific level."""
        if level not in self.levels:
            return False

        return self.levels[level].commit_event(event_id)

    def get_global_state(self, key: str = None) -> Dict[str, Any]:
        """Get global state, optionally filtered by key."""
        global_state = {}

        # Merge state from all levels (world level overrides lower levels)
        for level in sorted(self.levels.keys()):
            level_state = self.levels[level].state
            if key:
                if key in level_state:
                    global_state[key] = level_state[key]
            else:
                global_state.update(level_state)

        return global_state

    def get_causality_chain(self, event_id: str) -> List[LatticeEvent]:
        """Get the causal chain leading to an event."""
        chain = []
        visited = set()

        def traverse(eid: str):
            if eid in visited:
                return
            visited.add(eid)

            # Find event in log
            event = next((e for e in self.event_log if e.event_id == eid), None)
            if not event:
                return

            chain.append(event)
            for parent_id in event.parent_events:
                traverse(parent_id)

        traverse(event_id)
        return list(reversed(chain))

    def detect_conflicts(self) -> List[Tuple[LatticeEvent, LatticeEvent]]:
        """Detect conflicting events."""
        conflicts = []

        for i, event1 in enumerate(self.event_log):
            for event2 in self.event_log[i + 1 :]:
                # Same state key = potential conflict
                if event1.state_key == event2.state_key:
                    # Check if events are concurrent
                    if event1.vector_clock.concurrent_with(event2.vector_clock):
                        conflicts.append((event1, event2))

        return conflicts

    def get_lattice_structure(self) -> Dict[str, Any]:
        """Get the structure of the lattice."""
        return {
            'levels': {
                level_num: {
                    'name': level.name,
                    'domains': list(level.domains),
                    'total_events': len(level.events),
                    'committed_events': len(level.committed_events),
                    'pending_events': len(level.pending_events),
                }
                for level_num, level in self.levels.items()
            },
            'total_events_in_log': len(self.event_log),
            'detected_conflicts': len(self.detect_conflicts()),
        }

    def _determine_level(self, domain_id: str) -> int:
        """Determine which level a domain belongs to."""
        # Simple heuristic: find the lowest level containing this domain
        for level in sorted(self.levels.keys()):
            if domain_id in self.levels[level].domains:
                return level
        return 3  # Default to entity level

    def propagate_to_world(self, event_id: str) -> bool:
        """Propagate an event up to the world level."""
        # Find event
        event = next((e for e in self.event_log if e.event_id == event_id), None)
        if not event:
            return False

        # Create world-level event
        world_event = LatticeEvent(
            event_type=EventType.STATE_COMMIT,
            domain_id=self.world_domain_id or "world",
            state_key=event.state_key,
            state_value=event.state_value,
            parent_events=[event_id],
        )

        return self.submit_event(world_event)
