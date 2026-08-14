"""Multi-Domain Unification - Registry and Mesh Coordination

Manages the registry of all computational domains and orchestrates
cross-domain coordination through a unified mesh.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import uuid
from datetime import datetime


class DomainState(Enum):
    """Lifecycle states for a domain."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SYNCING = "syncing"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    SUSPENDED = "suspended"
    SHUTDOWN = "shutdown"


class DomainTier(Enum):
    """Hierarchical tier of a domain."""
    WORLD = "world"  # Global coordinator
    REGION = "region"  # Regional consensus node
    ZONE = "zone"  # Local domain cluster
    ENTITY = "entity"  # Individual entity/service


@dataclass
class DomainRegistration:
    """Registration record for a domain in the mesh."""
    domain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tier: DomainTier = DomainTier.ENTITY
    state: DomainState = DomainState.UNINITIALIZED
    parent_domain: Optional[str] = None
    child_domains: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeshEdge:
    """Connection between two domains in the mesh."""
    source: str
    destination: str
    capacity: int = 1000  # messages per second
    latency_ms: float = 0.0
    healthy: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainRegistry:
    """Registry of all active domains in the world kernel."""

    def __init__(self):
        self.domains: Dict[str, DomainRegistration] = {}
        self.world_domain_id: Optional[str] = None
        self.callbacks: Dict[str, List[Callable]] = {
            'domain_registered': [],
            'domain_state_changed': [],
            'domain_unregistered': [],
        }

    def register_domain(
        self,
        name: str,
        tier: DomainTier = DomainTier.ENTITY,
        parent_domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Register a new domain in the mesh."""
        registration = DomainRegistration(
            name=name,
            tier=tier,
            parent_domain=parent_domain,
            metadata=metadata or {},
        )

        if tier == DomainTier.WORLD:
            if self.world_domain_id is not None:
                raise ValueError("World domain already registered")
            self.world_domain_id = registration.domain_id

        self.domains[registration.domain_id] = registration

        # Update parent-child relationship
        if parent_domain and parent_domain in self.domains:
            self.domains[parent_domain].child_domains.append(registration.domain_id)

        # Trigger callbacks
        for callback in self.callbacks['domain_registered']:
            callback(registration)

        return registration.domain_id

    def get_domain(self, domain_id: str) -> Optional[DomainRegistration]:
        """Retrieve a domain registration."""
        return self.domains.get(domain_id)

    def update_domain_state(
        self,
        domain_id: str,
        new_state: DomainState,
    ) -> bool:
        """Update the state of a domain."""
        if domain_id not in self.domains:
            return False

        domain = self.domains[domain_id]
        old_state = domain.state
        domain.state = new_state
        domain.last_heartbeat = datetime.utcnow()

        # Trigger callbacks
        for callback in self.callbacks['domain_state_changed']:
            callback(domain_id, old_state, new_state)

        return True

    def get_domain_tree(self) -> Dict[str, Any]:
        """Get hierarchical tree of all domains."""
        if not self.world_domain_id:
            return {}

        def build_tree(domain_id: str) -> Dict[str, Any]:
            domain = self.domains[domain_id]
            return {
                'id': domain_id,
                'name': domain.name,
                'tier': domain.tier.value,
                'state': domain.state.value,
                'children': [
                    build_tree(child_id)
                    for child_id in domain.child_domains
                ],
            }

        return build_tree(self.world_domain_id)

    def list_domains_by_tier(self, tier: DomainTier) -> List[DomainRegistration]:
        """List all domains at a specific tier."""
        return [d for d in self.domains.values() if d.tier == tier]

    def unregister_domain(self, domain_id: str) -> bool:
        """Unregister a domain from the mesh."""
        if domain_id not in self.domains:
            return False

        domain = self.domains[domain_id]

        # Remove from parent's children list
        if domain.parent_domain and domain.parent_domain in self.domains:
            parent = self.domains[domain.parent_domain]
            if domain_id in parent.child_domains:
                parent.child_domains.remove(domain_id)

        del self.domains[domain_id]

        # Trigger callbacks
        for callback in self.callbacks['domain_unregistered']:
            callback(domain_id)

        return True


class MeshCoordinator:
    """Coordinates the mesh of domains, managing connections and routing."""

    def __init__(self, registry: DomainRegistry):
        self.registry = registry
        self.edges: Dict[str, MeshEdge] = {}
        self.routing_table: Dict[str, List[str]] = {}  # domain_id -> path to world

    def establish_connection(
        self,
        source: str,
        destination: str,
        capacity: int = 1000,
        latency_ms: float = 0.0,
    ) -> str:
        """Establish a connection between two domains."""
        edge_id = f"{source}→{destination}"
        edge = MeshEdge(
            source=source,
            destination=destination,
            capacity=capacity,
            latency_ms=latency_ms,
        )
        self.edges[edge_id] = edge
        self._rebuild_routing_table()
        return edge_id

    def disconnect(
        self,
        source: str,
        destination: str,
    ) -> bool:
        """Disconnect two domains."""
        edge_id = f"{source}→{destination}"
        if edge_id in self.edges:
            del self.edges[edge_id]
            self._rebuild_routing_table()
            return True
        return False

    def mark_edge_unhealthy(self, source: str, destination: str) -> bool:
        """Mark an edge as unhealthy (for failover)."""
        edge_id = f"{source}→{destination}"
        if edge_id in self.edges:
            self.edges[edge_id].healthy = False
            self._rebuild_routing_table()
            return True
        return False

    def mark_edge_healthy(self, source: str, destination: str) -> bool:
        """Mark an edge as healthy (recovery)."""
        edge_id = f"{source}→{destination}"
        if edge_id in self.edges:
            self.edges[edge_id].healthy = True
            self._rebuild_routing_table()
            return True
        return False

    def get_route_to_world(self, domain_id: str) -> Optional[List[str]]:
        """Get the path from a domain to the world domain."""
        return self.routing_table.get(domain_id)

    def get_mesh_health(self) -> Dict[str, Any]:
        """Get overall health of the mesh."""
        total_edges = len(self.edges)
        healthy_edges = sum(1 for e in self.edges.values() if e.healthy)
        total_capacity = sum(e.capacity for e in self.edges.values())
        avg_latency = (
            sum(e.latency_ms for e in self.edges.values()) / total_edges
            if total_edges > 0 else 0
        )

        return {
            'total_edges': total_edges,
            'healthy_edges': healthy_edges,
            'health_percentage': (healthy_edges / total_edges * 100) if total_edges > 0 else 0,
            'total_capacity': total_capacity,
            'average_latency_ms': avg_latency,
        }

    def _rebuild_routing_table(self):
        """Rebuild routing table using BFS from world domain."""
        if not self.registry.world_domain_id:
            return

        self.routing_table = {}
        visited = set()
        queue = [(self.registry.world_domain_id, [self.registry.world_domain_id])]

        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for edge_id, edge in self.edges.items():
                if not edge.healthy:
                    continue

                # Check if this edge connects from current
                if edge.source == current and edge.destination not in visited:
                    new_path = path + [edge.destination]
                    self.routing_table[edge.destination] = new_path
                    queue.append((edge.destination, new_path))


class DomainLifecycleManager:
    """Manages the lifecycle of domains from initialization to shutdown."""

    def __init__(self, registry: DomainRegistry, coordinator: MeshCoordinator):
        self.registry = registry
        self.coordinator = coordinator
        self.initialization_hooks: Dict[str, List[Callable]] = {}
        self.shutdown_hooks: Dict[str, List[Callable]] = {}

    def register_init_hook(
        self,
        domain_id: str,
        hook: Callable[[DomainRegistration], Any],
    ):
        """Register a hook to run when a domain initializes."""
        if domain_id not in self.initialization_hooks:
            self.initialization_hooks[domain_id] = []
        self.initialization_hooks[domain_id].append(hook)

    def register_shutdown_hook(
        self,
        domain_id: str,
        hook: Callable[[DomainRegistration], Any],
    ):
        """Register a hook to run when a domain shuts down."""
        if domain_id not in self.shutdown_hooks:
            self.shutdown_hooks[domain_id] = []
        self.shutdown_hooks[domain_id].append(hook)

    def initialize_domain(self, domain_id: str) -> bool:
        """Initialize a domain."""
        domain = self.registry.get_domain(domain_id)
        if not domain:
            return False

        self.registry.update_domain_state(domain_id, DomainState.INITIALIZING)

        # Run initialization hooks
        for hook in self.initialization_hooks.get(domain_id, []):
            try:
                hook(domain)
            except Exception as e:
                print(f"Error in init hook for domain {domain_id}: {e}")

        self.registry.update_domain_state(domain_id, DomainState.ACTIVE)
        return True

    def shutdown_domain(self, domain_id: str) -> bool:
        """Shutdown a domain."""
        domain = self.registry.get_domain(domain_id)
        if not domain:
            return False

        self.registry.update_domain_state(domain_id, DomainState.SHUTDOWN)

        # Run shutdown hooks
        for hook in self.shutdown_hooks.get(domain_id, []):
            try:
                hook(domain)
            except Exception as e:
                print(f"Error in shutdown hook for domain {domain_id}: {e}")

        return True
