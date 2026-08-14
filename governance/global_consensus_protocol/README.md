# Global Consensus Protocol - Hierarchical BFT

The planetary agreement engine for Portal-OS v3/v4.1.

This protocol ensures global consensus across all domains while maintaining:
- Byzantine fault tolerance (up to 1/3 malicious nodes)
- Hierarchical decision-making (World → Region → Zone → Entity)
- Planetary-scale consistency
- Governance integration
- Identity verification

## Components

### 1. hierarchical_bft/
Byzantine Fault Tolerant consensus:
- Multi-phase voting (pre-prepare, prepare, commit)
- Leader election and failover
- View change protocol
- Batch optimization

### 2. consensus_coordinator/
Global consensus orchestration:
- Multi-tier consensus execution
- Tiebreaker mechanisms
- Health monitoring
- Consensus state machine

### 3. world_governance_protocol/
Decentralized governance:
- Proposal system
- Hierarchical voting
- Constitution engine
- Lawbook registry

### 4. world_identity_consensus/
Identity verification across domains:
- Distributed identity validation
- Cryptographic proof validation
- Identity registration
- Multi-signature support

## Status
- [x] Module structure
- [x] BFT protocol
- [x] Consensus coordinator
- [x] Governance protocol
- [x] Identity consensus
- [ ] Integration with world kernel
- [ ] Testing suite
