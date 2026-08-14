"""World Consensus Coordinator - Global Consensus Orchestration"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
from datetime import datetime
from collections import defaultdict


class ConsensusState(Enum):
    IDLE = "idle"
    PROPOSING = "proposing"
    VOTING = "voting"
    COMMITTING = "committing"
    COMMITTED = "committed"
    FAILED = "failed"


class TieredConsensusLevel(Enum):
    WORLD = "world"
    REGION = "region"
    ZONE = "zone"
    ENTITY = "entity"


@dataclass
class ConsensusResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str = ""
    level: TieredConsensusLevel = TieredConsensusLevel.WORLD
    state: ConsensusState = ConsensusState.IDLE
    approved: bool = False
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TieredConsensusRound:
    round_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: TieredConsensusLevel = TieredConsensusLevel.WORLD
    proposal_id: str = ""
    participants: Set[str] = field(default_factory=set)
    state: ConsensusState = ConsensusState.IDLE
    start_time: datetime = field(default_factory=datetime.utcnow)
    timeout: int = 30
    required_threshold: float = 0.67


class WorldConsensusCoordinator:
    def __init__(self):
        self.active_rounds: Dict[str, TieredConsensusRound] = {}
        self.completed_results: List[ConsensusResult] = []
        self.tier_consensus_nodes: Dict[TieredConsensusLevel, Set[str]] = {
            TieredConsensusLevel.WORLD: set(),
            TieredConsensusLevel.REGION: set(),
            TieredConsensusLevel.ZONE: set(),
            TieredConsensusLevel.ENTITY: set(),
        }
        self.escalation_queue: List[str] = []

    def register_consensus_node(self, node_id: str, level: TieredConsensusLevel) -> bool:
        self.tier_consensus_nodes[level].add(node_id)
        return True

    def initiate_consensus(self, proposal_id: str, start_level: TieredConsensusLevel = TieredConsensusLevel.ENTITY) -> str:
        round_id = str(uuid.uuid4())
        participants = self.tier_consensus_nodes[start_level]
        consensus_round = TieredConsensusRound(
            round_id=round_id,
            level=start_level,
            proposal_id=proposal_id,
            participants=participants,
        )
        self.active_rounds[round_id] = consensus_round
        return round_id

    def finalize_consensus(self, round_id: str, votes_for: int, votes_against: int, votes_abstain: int) -> Optional[ConsensusResult]:
        if round_id not in self.active_rounds:
            return None
        consensus_round = self.active_rounds[round_id]
        total_votes = votes_for + votes_against + votes_abstain
        if total_votes == 0:
            return None
        approval_ratio = votes_for / total_votes
        approved = approval_ratio >= consensus_round.required_threshold
        result = ConsensusResult(
            proposal_id=consensus_round.proposal_id,
            level=consensus_round.level,
            state=ConsensusState.COMMITTED,
            approved=approved,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_abstain=votes_abstain,
            completed_at=datetime.utcnow(),
        )
        self.completed_results.append(result)
        del self.active_rounds[round_id]
        return result

    def get_consensus_health(self) -> Dict[str, Any]:
        completed = len(self.completed_results)
        approved = sum(1 for r in self.completed_results if r.approved)
        return {
            'active_rounds': len(self.active_rounds),
            'completed_decisions': completed,
            'approved_decisions': approved,
            'approval_rate': (approved / completed * 100) if completed > 0 else 0,
        }
