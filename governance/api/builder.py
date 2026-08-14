"""
Governance API Builder v1
Registers governance API endpoints.
"""

from governance.api.server import GovernanceApiServer

def build_governance_api(lawbook_engine):
    api = GovernanceApiServer(lawbook_engine)

    api.add_route("/rules", lambda payload: lawbook_engine.evaluate_rules(payload))
    api.add_route("/invariants", lambda payload: lawbook_engine.check_invariants(payload))
    api.add_route("/escalate", lambda payload: lawbook_engine.escalate(payload))
    api.add_route("/describe", lambda payload: lawbook_engine.describe())

    return api
