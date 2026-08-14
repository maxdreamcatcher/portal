"""World Identity Consensus - Distributed Identity Verification"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import uuid
from datetime import datetime, timedelta


class IdentityStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class IdentityType(Enum):
    DOMAIN = "domain"
    ENTITY = "entity"
    SERVICE = "service"
    USER = "user"


@dataclass
class CryptographicProof:
    proof_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str = ""
    proof_type: str = ""
    public_key: str = ""
    signature: str = ""
    verified: bool = False


@dataclass
class DistributedIdentity:
    identity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    identity_type: IdentityType = IdentityType.DOMAIN
    owner_domain: str = ""
    status: IdentityStatus = IdentityStatus.PENDING
    verifications: Dict[str, bool] = field(default_factory=dict)


class IdentityConsensusValidator:
    def __init__(self, required_validators: int = 3):
        self.identities: Dict[str, DistributedIdentity] = {}
        self.validators: Set[str] = set()
        self.required_validators = required_validators

    def register_identity(self, name: str, identity_type: IdentityType, owner_domain: str) -> str:
        identity = DistributedIdentity(
            name=name,
            identity_type=identity_type,
            owner_domain=owner_domain,
        )
        self.identities[identity.identity_id] = identity
        return identity.identity_id

    def register_validator(self, validator_id: str) -> bool:
        self.validators.add(validator_id)
        return True

    def submit_verification(self, identity_id: str, validator_id: str, verified: bool) -> bool:
        if identity_id not in self.identities:
            return False
        identity = self.identities[identity_id]
        identity.verifications[validator_id] = verified
        verified_count = sum(1 for v in identity.verifications.values() if v)
        total_votes = len(identity.verifications)
        if total_votes >= self.required_validators and verified_count >= (total_votes * 2 / 3):
            identity.status = IdentityStatus.VERIFIED
        return True

    def get_identity(self, identity_id: str) -> Optional[DistributedIdentity]:
        return self.identities.get(identity_id)


class IdentityRegistrar:
    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}

    def register_identity_globally(self, identity_id: str, identity_data: Dict[str, Any]) -> bool:
        self.registry[identity_id] = identity_data
        return True

    def lookup_identity(self, identity_id: str) -> Optional[Dict[str, Any]]:
        return self.registry.get(identity_id)
