"""World Entities - Entity Lifecycle and Behavior

Manages entity creation, destruction, state transitions, and behavior execution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import uuid
from datetime import datetime


class EntityState(Enum):
    """States of an entity."""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    EXECUTING = "executing"
    TRANSITIONING = "transitioning"
    SUSPENDED = "suspended"
    DESTROYED = "destroyed"


class BehaviorResult(Enum):
    """Result of behavior execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class EntityBehavior:
    """A behavior that an entity can execute."""
    behavior_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    priority: int = 0
    enabled: bool = True
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTransition:
    """A transition between entity states."""
    from_state: EntityState
    to_state: EntityState
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorldEntity:
    """An entity in the world simulation."""
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    entity_type: str = "generic"
    state: EntityState = EntityState.INACTIVE
    position: tuple = (0, 0, 0)
    velocity: tuple = (0, 0, 0)
    behaviors: Dict[str, EntityBehavior] = field(default_factory=dict)
    state_machine: Dict[EntityState, List[StateTransition]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_entity: Optional[str] = None
    child_entities: List[str] = field(default_factory=list)

    def transition_to(self, new_state: EntityState) -> bool:
        """Transition to a new state."""
        transitions = self.state_machine.get(self.state, [])
        for transition in transitions:
            if transition.to_state == new_state:
                if transition.condition is None or transition.condition(self):
                    if transition.action:
                        transition.action(self)
                    self.state = new_state
                    self.updated_at = datetime.utcnow()
                    return True
        return False

    def add_behavior(self, behavior: EntityBehavior) -> bool:
        """Add a behavior to the entity."""
        self.behaviors[behavior.behavior_id] = behavior
        return True

    def add_child(self, child_id: str) -> bool:
        """Add a child entity."""
        self.child_entities.append(child_id)
        return True


class EntityManager:
    """Manages all entities in the world."""

    def __init__(self):
        self.entities: Dict[str, WorldEntity] = {}
        self.entity_index: Dict[str, List[str]] = {}  # type -> [entity_ids]
        self.active_entities: Set[str] = set()
        self.entity_events: Dict[str, List[Callable]] = {}  # entity_id -> callbacks

    def create_entity(
        self,
        name: str,
        entity_type: str = "generic",
        position: tuple = (0, 0, 0),
    ) -> str:
        """Create a new entity."""
        entity = WorldEntity(
            name=name,
            entity_type=entity_type,
            position=position,
        )
        self.entities[entity.entity_id] = entity

        if entity_type not in self.entity_index:
            self.entity_index[entity_type] = []
        self.entity_index[entity_type].append(entity.entity_id)

        return entity.entity_id

    def destroy_entity(self, entity_id: str) -> bool:
        """Destroy an entity."""
        if entity_id not in self.entities:
            return False

        entity = self.entities[entity_id]
        entity.state = EntityState.DESTROYED
        self.active_entities.discard(entity_id)
        del self.entities[entity_id]
        return True

    def activate_entity(self, entity_id: str) -> bool:
        """Activate an entity."""
        if entity_id not in self.entities:
            return False

        entity = self.entities[entity_id]
        entity.state = EntityState.ACTIVE
        self.active_entities.add(entity_id)
        return True

    def get_entity(self, entity_id: str) -> Optional[WorldEntity]:
        """Get an entity."""
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[WorldEntity]:
        """Get all entities of a type."""
        entity_ids = self.entity_index.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]

    def update_entities(self, dt: float) -> None:
        """Update all active entities."""
        for entity_id in list(self.active_entities):
            entity = self.entities.get(entity_id)
            if entity:
                self._execute_behaviors(entity, dt)

    def _execute_behaviors(self, entity: WorldEntity, dt: float) -> None:
        """Execute all behaviors for an entity."""
        # Sort behaviors by priority
        sorted_behaviors = sorted(
            entity.behaviors.values(),
            key=lambda b: b.priority,
            reverse=True,
        )

        for behavior in sorted_behaviors:
            if not behavior.enabled:
                continue

            # Check condition
            if behavior.condition and not behavior.condition(entity):
                continue

            # Execute action
            if behavior.action:
                try:
                    result = behavior.action(entity, dt)
                    entity.updated_at = datetime.utcnow()
                except Exception as e:
                    print(f"Error executing behavior {behavior.name}: {e}")

    def get_entity_tree(self, entity_id: str) -> Dict[str, Any]:
        """Get hierarchical tree of entity and children."""
        entity = self.entities.get(entity_id)
        if not entity:
            return {}

        return {
            'id': entity_id,
            'name': entity.name,
            'type': entity.entity_type,
            'state': entity.state.value,
            'children': [
                self.get_entity_tree(child_id)
                for child_id in entity.child_entities
            ],
        }
