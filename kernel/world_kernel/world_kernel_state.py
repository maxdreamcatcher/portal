"""World Kernel State - Global State Management

Manages the global state of the world kernel with distributed synchronization,
conflict resolution, and consistency guarantees.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
from datetime import datetime
from copy import deepcopy


class ConsistencyLevel(Enum):
    """Consistency guarantees for state."""
    EVENTUAL = "eventual"  # Weak consistency
    CAUSAL = "causal"  # Preserves causality
    STRONG = "strong"  # Immediate global consistency
    LINEARIZABLE = "linearizable"  # Strongest consistency


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving concurrent state updates."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    HIGHEST_PRIORITY = "highest_priority"
    CUSTOM = "custom"  # User-defined


@dataclass
class StateUpdate:
    """An update to global state."""
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: str = ""
    state_path: str = ""  # e.g., "world.domains.zone1.entity2"
    old_value: Any = None
    new_value: Any = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Higher = more important
    committed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateConflict:
    """A conflict between two concurrent state updates."""
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    updates: List[StateUpdate] = field(default_factory=list)
    state_path: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution: Optional[StateUpdate] = None


class StateNode:
    """A node in the hierarchical state tree."""

    def __init__(self, name: str, parent: Optional['StateNode'] = None):
        self.name = name
        self.parent = parent
        self.children: Dict[str, 'StateNode'] = {}
        self.value: Any = None
        self.version: int = 0
        self.last_updated: datetime = datetime.utcnow()
        self.owner_domain: str = ""

    def get_path(self) -> str:
        """Get the full path of this node."""
        if not self.parent:
            return self.name
        return f"{self.parent.get_path()}.{self.name}"

    def get_value(self) -> Any:
        """Get the value at this node."""
        if self.children:
            return {name: child.get_value() for name, child in self.children.items()}
        return self.value

    def set_value(self, value: Any, domain_id: str) -> bool:
        """Set the value at this node."""
        self.value = value
        self.version += 1
        self.last_updated = datetime.utcnow()
        self.owner_domain = domain_id
        return True

    def create_child(self, name: str) -> 'StateNode':
        """Create a child node."""
        if name not in self.children:
            self.children[name] = StateNode(name, self)
        return self.children[name]

    def get_or_create_path(self, path: str) -> 'StateNode':
        """Navigate or create a path in the tree."""
        parts = path.split('.')
        node = self
        for part in parts:
            node = node.create_child(part)
        return node


class WorldKernelState:
    """Global state manager for the world kernel."""

    def __init__(
        self,
        consistency_level: ConsistencyLevel = ConsistencyLevel.CAUSAL,
    ):
        self.root = StateNode("world")
        self.consistency_level = consistency_level
        self.updates_log: List[StateUpdate] = []
        self.conflicts: Dict[str, StateConflict] = {}
        self.resolution_strategy = ConflictResolutionStrategy.LAST_WRITE_WINS
        self.custom_resolver: Optional[Callable] = None
        self.snapshots: Dict[str, Dict[str, Any]] = {}  # snapshot_id -> state
        self.watchers: Dict[str, List[Callable]] = {}  # path -> callbacks
        self.access_control: Dict[str, Set[str]] = {}  # path -> allowed_domains

    def update_state(
        self,
        state_path: str,
        new_value: Any,
        domain_id: str,
        priority: int = 0,
    ) -> Optional[str]:
        """Update global state at a path."""
        # Check access control
        if not self._check_access(state_path, domain_id):
            return None

        # Get current value
        node = self.root.get_or_create_path(state_path)
        old_value = node.value

        # Create update record
        update = StateUpdate(
            domain_id=domain_id,
            state_path=state_path,
            old_value=old_value,
            new_value=new_value,
            priority=priority,
        )

        # Add to log
        self.updates_log.append(update)

        # Apply update
        node.set_value(new_value, domain_id)
        update.committed = True

        # Trigger watchers
        self._notify_watchers(state_path, old_value, new_value)

        return update.update_id

    def detect_conflict(self, update1: StateUpdate, update2: StateUpdate) -> Optional[StateConflict]:
        """Detect if two updates conflict."""
        # Same path and concurrent updates = conflict
        if update1.state_path != update2.state_path:
            return None

        # Check if updates overlap in time (concurrent)
        if update1.timestamp <= update2.timestamp <= update1.timestamp:
            return None  # Sequential

        # Conflict detected
        conflict = StateConflict(
            updates=[update1, update2],
            state_path=update1.state_path,
        )
        self.conflicts[conflict.conflict_id] = conflict
        return conflict

    def resolve_conflict(
        self,
        conflict_id: str,
    ) -> Optional[StateUpdate]:
        """Resolve a detected conflict."""
        if conflict_id not in self.conflicts:
            return None

        conflict = self.conflicts[conflict_id]
        if conflict.resolved:
            return conflict.resolution

        # Use resolution strategy
        if self.resolution_strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            resolution = max(conflict.updates, key=lambda u: u.timestamp)
        elif self.resolution_strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            resolution = min(conflict.updates, key=lambda u: u.timestamp)
        elif self.resolution_strategy == ConflictResolutionStrategy.HIGHEST_PRIORITY:
            resolution = max(conflict.updates, key=lambda u: u.priority)
        elif self.resolution_strategy == ConflictResolutionStrategy.CUSTOM:
            if self.custom_resolver:
                resolution = self.custom_resolver(conflict.updates)
            else:
                resolution = conflict.updates[0]
        else:
            resolution = conflict.updates[0]

        conflict.resolution = resolution
        conflict.resolved = True

        # Apply resolution
        node = self.root.get_or_create_path(resolution.state_path)
        node.set_value(resolution.new_value, resolution.domain_id)

        return resolution

    def get_state(self, state_path: str = None) -> Any:
        """Get state at a path."""
        if not state_path:
            return self.root.get_value()

        node = self.root.get_or_create_path(state_path)
        return node.get_value()

    def create_snapshot(self) -> str:
        """Create a snapshot of current state."""
        snapshot_id = str(uuid.uuid4())
        self.snapshots[snapshot_id] = deepcopy(self._serialize_state())
        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore state from a snapshot."""
        if snapshot_id not in self.snapshots:
            return False

        snapshot_data = self.snapshots[snapshot_id]
        self.root = self._deserialize_state(snapshot_data)
        return True

    def watch_path(
        self,
        state_path: str,
        callback: Callable[[Any, Any], None],
    ) -> str:
        """Watch for changes at a state path."""
        if state_path not in self.watchers:
            self.watchers[state_path] = []
        self.watchers[state_path].append(callback)
        return str(uuid.uuid4())

    def set_access_control(
        self,
        state_path: str,
        allowed_domains: Set[str],
    ):
        """Set access control for a state path."""
        self.access_control[state_path] = allowed_domains

    def get_audit_log(
        self,
        state_path: str = None,
        domain_id: str = None,
    ) -> List[StateUpdate]:
        """Get audit log filtered by path and/or domain."""
        log = self.updates_log

        if state_path:
            log = [u for u in log if u.state_path == state_path]
        if domain_id:
            log = [u for u in log if u.domain_id == domain_id]

        return log

    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about state management."""
        return {
            'total_updates': len(self.updates_log),
            'total_conflicts': len(self.conflicts),
            'resolved_conflicts': sum(1 for c in self.conflicts.values() if c.resolved),
            'unresolved_conflicts': sum(1 for c in self.conflicts.values() if not c.resolved),
            'total_snapshots': len(self.snapshots),
            'watched_paths': len(self.watchers),
            'access_controlled_paths': len(self.access_control),
            'consistency_level': self.consistency_level.value,
        }

    def _check_access(self, state_path: str, domain_id: str) -> bool:
        """Check if domain has access to a state path."""
        if state_path not in self.access_control:
            return True  # No restriction
        return domain_id in self.access_control[state_path]

    def _notify_watchers(self, state_path: str, old_value: Any, new_value: Any):
        """Notify all watchers of a state change."""
        callbacks = self.watchers.get(state_path, [])
        for callback in callbacks:
            try:
                callback(old_value, new_value)
            except Exception as e:
                print(f"Error in state watcher: {e}")

    def _serialize_state(self) -> Dict[str, Any]:
        """Serialize the state tree."""
        def serialize_node(node: StateNode) -> Dict[str, Any]:
            return {
                'name': node.name,
                'value': node.value,
                'version': node.version,
                'owner_domain': node.owner_domain,
                'children': {
                    name: serialize_node(child)
                    for name, child in node.children.items()
                },
            }

        return serialize_node(self.root)

    def _deserialize_state(self, data: Dict[str, Any]) -> StateNode:
        """Deserialize state tree from data."""
        def deserialize_node(
            node_data: Dict[str, Any],
            parent: Optional[StateNode] = None,
        ) -> StateNode:
            node = StateNode(node_data['name'], parent)
            node.value = node_data.get('value')
            node.version = node_data.get('version', 0)
            node.owner_domain = node_data.get('owner_domain', '')

            for child_name, child_data in node_data.get('children', {}).items():
                node.children[child_name] = deserialize_node(child_data, node)

            return node

        return deserialize_node(data)
