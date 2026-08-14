"""World Governance Protocol - Decentralized Governance"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
from datetime import datetime, timedelta
from collections import defaultdict


class ProposalStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACTIVE = "active"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProposalType(Enum):
    CONSTITUTION_AMENDMENT = "constitution_amendment"
    LAW_ENACTMENT = "law_enactment"
    PARAMETER_CHANGE = "parameter_change"
    EMERGENCY_ACTION = "emergency_action"


@dataclass
class GovernanceProposal:
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer_domain: str = ""
    title: str = ""
    description: str = ""
    proposal_type: ProposalType = ProposalType.LAW_ENACTMENT
    status: ProposalStatus = ProposalStatus.DRAFT
    content: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    voting_deadline: Optional[datetime] = None
    votes_for: int = 0
    votes_against: int = 0


class GovernanceProposalEngine:
    def __init__(self):
        self.proposals: Dict[str, GovernanceProposal] = {}
        self.proposal_queue: List[str] = []

    def create_proposal(self, proposer_domain: str, title: str, description: str, proposal_type: ProposalType, content: Dict[str, Any]) -> str:
        proposal = GovernanceProposal(
            proposer_domain=proposer_domain,
            title=title,
            description=description,
            proposal_type=proposal_type,
            content=content,
        )
        self.proposals[proposal.proposal_id] = proposal
        return proposal.proposal_id

    def submit_proposal(self, proposal_id: str) -> bool:
        if proposal_id not in self.proposals:
            return False
        proposal = self.proposals[proposal_id]
        proposal.status = ProposalStatus.SUBMITTED
        proposal.voting_deadline = datetime.utcnow() + timedelta(days=7)
        self.proposal_queue.append(proposal_id)
        return True

    def get_proposal(self, proposal_id: str) -> Optional[GovernanceProposal]:
        return self.proposals.get(proposal_id)


class LawbookRegistry:
    def __init__(self):
        self.laws: Dict[str, Dict[str, Any]] = {}
        self.precedents: Dict[str, Dict[str, Any]] = {}

    def register_law(self, law_id: str, content: Dict[str, Any]) -> bool:
        self.laws[law_id] = content
        return True

    def record_precedent(self, precedent_id: str, ruling: Dict[str, Any]) -> bool:
        self.precedents[precedent_id] = ruling
        return True
