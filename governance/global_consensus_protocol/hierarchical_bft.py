"""Hierarchical Byzantine Fault Tolerant (BFT) Consensus

Implements a hierarchical BFT protocol that operates across multiple tiers
of domains, maintaining Byzantine fault tolerance at each level.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import uuid
from datetime import datetime, timedelta
from collections import defaultdict


class BFTPhase(Enum):
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    VIEW_CHANGE = "view_change"


class BFTMessageType(Enum):
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    REPLY = "reply"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"


class NodeRole(Enum):
    PRIMARY = "primary"
    BACKUP = "backup"
    AUDITOR = "auditor"


@dataclass
class BFTMessage:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: BFTMessageType = BFTMessageType.PRE_PREPARE
    view_number: int = 0
    sequence_number: int = 0
    sender_node: str = ""
    payload: Any = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusProposal:
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer: str = ""
    content: Any = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BFTNode:
    def __init__(self, node_id: str, role: NodeRole = NodeRole.BACKUP, fault_tolerance: int = 1):
        self.node_id = node_id
        self.role = role
        self.fault_tolerance = fault_tolerance
        self.view_number = 0
        self.sequence_number = 0
        self.received_messages: Dict[str, BFTMessage] = {}
        self.sent_messages: List[BFTMessage] = []
        self.prepare_messages: Dict[str, Set[str]] = defaultdict(set)
        self.commit_messages: Dict[str, Set[str]] = defaultdict(set)
        self.committed_proposals: List[ConsensusProposal] = []
        self.pending_proposals: List[ConsensusProposal] = []
        self.watermark_low = 0
        self.watermark_high = 1000
        self.callbacks: Dict[str, List[Callable]] = {
            'message_received': [],
            'proposal_committed': [],
            'view_changed': [],
        }

    def on_pre_prepare(self, view: int, sequence: int, proposal: ConsensusProposal) -> bool:
        if view < self.view_number:
            return False
        if sequence < self.watermark_low or sequence > self.watermark_high:
            return False
        self.pending_proposals.append(proposal)
        prepare_msg = BFTMessage(
            message_type=BFTMessageType.PREPARE,
            view_number=view,
            sequence_number=sequence,
            sender_node=self.node_id,
            payload=proposal,
        )
        self.sent_messages.append(prepare_msg)
        return True

    def on_prepare(self, view: int, sequence: int, sender: str) -> bool:
        if view < self.view_number:
            return False
        if sequence < self.watermark_low or sequence > self.watermark_high:
            return False
        key = f"{view}:{sequence}"
        self.prepare_messages[key].add(sender)
        required_prepares = 2 * self.fault_tolerance + 1
        return len(self.prepare_messages[key]) >= required_prepares

    def on_commit(self, view: int, sequence: int, sender: str) -> bool:
        if view < self.view_number:
            return False
        key = f"{view}:{sequence}"
        self.commit_messages[key].add(sender)
        required_commits = 2 * self.fault_tolerance + 1
        if len(self.commit_messages[key]) >= required_commits:
            proposal = next((p for p in self.pending_proposals), None)
            if proposal:
                self.committed_proposals.append(proposal)
                self.pending_proposals.remove(proposal)
                return True
        return False

    def get_consensus_state(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'role': self.role.value,
            'view_number': self.view_number,
            'sequence_number': self.sequence_number,
            'committed_proposals': len(self.committed_proposals),
            'pending_proposals': len(self.pending_proposals),
        }


class BFTConsensusRound:
    def __init__(self, round_id: str, view_number: int, nodes: List[BFTNode], proposal: ConsensusProposal):
        self.round_id = round_id
        self.view_number = view_number
        self.nodes = nodes
        self.proposal = proposal
        self.phase = BFTPhase.PRE_PREPARE
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.outcome: Optional[bool] = None

    def execute_round(self) -> bool:
        primary = next((n for n in self.nodes if n.role == NodeRole.PRIMARY), None)
        if not primary:
            return False
        for node in self.nodes:
            if node != primary:
                node.on_pre_prepare(self.view_number, 0, self.proposal)
        self.phase = BFTPhase.PREPARE
        for node in self.nodes:
            node.on_prepare(self.view_number, 0, primary.node_id)
        self.phase = BFTPhase.COMMIT
        for node in self.nodes:
            node.on_commit(self.view_number, 0, node.node_id)
        committed_count = sum(1 for node in self.nodes if self.proposal in node.committed_proposals)
        required = len(self.nodes) - (len(self.nodes) // 3)
        self.outcome = committed_count >= required
        self.end_time = datetime.utcnow()
        return self.outcome
