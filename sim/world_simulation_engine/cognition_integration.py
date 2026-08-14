"""Cognition Integration - SIM/Cognitive Mesh Binding

Integrates the world simulation with the cognitive/AI layer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
from datetime import datetime


class CognitionUpdateType(Enum):
    """Type of cognition update."""
    OBSERVATION = "observation"
    LEARNING = "learning"
    DECISION = "decision"
    ADAPTATION = "adaptation"
    EMERGENCE = "emergence"


@dataclass
class CognitionObservation:
    """An observation from the simulation for the cognitive layer."""
    observation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    update_type: CognitionUpdateType = CognitionUpdateType.OBSERVATION
    source_entity: str = ""
    observed_entities: List[str] = field(default_factory=list)
    observation_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    simulation_time: float = 0.0


@dataclass
class CognitionFeedback:
    """Feedback from the cognitive layer back to simulation."""
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cognitive_agent: str = ""
    decision: str = ""
    decision_confidence: float = 0.0
    recommended_action: Optional[Callable] = None
    learning_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class CognitionIntegrator:
    """Integrates simulation with cognitive layer."""

    def __init__(self):
        self.cognitive_agents: Set[str] = set()
        self.observation_queue: List[CognitionObservation] = []
        self.feedback_queue: List[CognitionFeedback] = []
        self.agent_models: Dict[str, Dict[str, Any]] = {}  # agent_id -> learned_model
        self.emergence_events: List[Dict[str, Any]] = []
        self.cognitive_state: Dict[str, Any] = {}

    def register_cognitive_agent(self, agent_id: str) -> bool:
        """Register a cognitive agent with the integrator."""
        self.cognitive_agents.add(agent_id)
        self.agent_models[agent_id] = {}
        return True

    def send_observation(
        self,
        source_entity: str,
        observed_entities: List[str],
        observation_data: Dict[str, Any],
        simulation_time: float,
    ) -> str:
        """Send an observation from simulation to cognitive layer."""
        observation = CognitionObservation(
            source_entity=source_entity,
            observed_entities=observed_entities,
            observation_data=observation_data,
            simulation_time=simulation_time,
        )
        self.observation_queue.append(observation)
        return observation.observation_id

    def receive_feedback(
        self,
        cognitive_agent: str,
        decision: str,
        decision_confidence: float,
        learning_data: Dict[str, Any] = None,
    ) -> str:
        """Receive feedback from cognitive layer."""
        feedback = CognitionFeedback(
            cognitive_agent=cognitive_agent,
            decision=decision,
            decision_confidence=decision_confidence,
            learning_data=learning_data or {},
        )
        self.feedback_queue.append(feedback)
        return feedback.feedback_id

    def process_observations(self) -> int:
        """Process all pending observations."""
        count = len(self.observation_queue)
        for observation in self.observation_queue:
            # Forward to cognitive agents
            for agent_id in self.cognitive_agents:
                # In real implementation, would call cognitive agent
                pass
        self.observation_queue.clear()
        return count

    def process_feedback(self) -> int:
        """Process all pending feedback from cognitive layer."""
        count = len(self.feedback_queue)
        for feedback in self.feedback_queue:
            # Update agent model with learning data
            if feedback.cognitive_agent in self.agent_models:
                self.agent_models[feedback.cognitive_agent].update(
                    feedback.learning_data
                )
        self.feedback_queue.clear()
        return count

    def detect_emergent_behavior(
        self,
        pattern: str,
        entities: List[str],
        confidence: float,
    ) -> str:
        """Detect emergent behavior in the simulation."""
        emergence_event = {
            'pattern': pattern,
            'entities': entities,
            'confidence': confidence,
            'timestamp': datetime.utcnow(),
        }
        self.emergence_events.append(emergence_event)
        return str(uuid.uuid4())

    def get_cognitive_state(self) -> Dict[str, Any]:
        """Get current cognitive system state."""
        return {
            'registered_agents': len(self.cognitive_agents),
            'pending_observations': len(self.observation_queue),
            'pending_feedback': len(self.feedback_queue),
            'emergence_events': len(self.emergence_events),
            'agent_models': {
                agent_id: len(model)
                for agent_id, model in self.agent_models.items()
            },
        }
