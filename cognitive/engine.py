"""
Cognitive Engine v1
Registry + dispatcher + session manager.
"""

from cognitive.domain import CognitiveDomain
from cognitive.session import CognitiveSession

class CognitiveEngine:
    def __init__(self):
        self.domains = {}
        self.sessions = {}

    def register_domain(self, name, description="", metadata=None):
        domain = CognitiveDomain(name, description, metadata)
        self.domains[name] = domain
        return domain

    def get_domain(self, name):
        return self.domains.get(name)

    def create_session(self, domain_name, session_id, metadata=None):
        if domain_name not in self.domains:
            return {"error": "domain_not_found"}
        session = CognitiveSession(session_id, domain_name, metadata)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def run(self, domain_name, function_name, session_id, payload):
        domain = self.get_domain(domain_name)
        if not domain:
            return {"error": "domain_not_found"}

        func = domain.get_function(function_name)
        if not func:
            return {"error": "function_not_found"}

        session = self.get_session(session_id)
        if not session:
            return {"error": "session_not_found"}

        result = func.run(session, payload)
        session.record({
            "function": function_name,
            "payload": payload,
            "result": result["result"]
        })
        return {
            "domain": domain_name,
            "session": session_id,
            "function": function_name,
            "result": result["result"]
        }

    def describe(self):
        return {
            "domains": {name: d.describe() for name, d in self.domains.items()},
            "sessions": {sid: s.describe() for sid, s in self.sessions.items()}
        }
