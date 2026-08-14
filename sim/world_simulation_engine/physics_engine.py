"""Physics Engine - Core Physics Simulation Primitives

Implements basic physics primitives for world simulation including
forces, momentum, velocity, and collision detection.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import uuid
from datetime import datetime
import math


class PhysicsObjectType(Enum):
    """Type of physics object."""
    RIGID_BODY = "rigid_body"
    SOFT_BODY = "soft_body"
    PARTICLE = "particle"
    FORCE_FIELD = "force_field"


class CollisionType(Enum):
    """Type of collision."""
    ELASTIC = "elastic"
    INELASTIC = "inelastic"
    PERFECTLY_INELASTIC = "perfectly_inelastic"


@dataclass
class Vector3:
    """3D Vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> 'Vector3':
        mag = self.magnitude()
        if mag == 0:
            return Vector3()
        return Vector3(self.x/mag, self.y/mag, self.z/mag)

    def dot(self, other: 'Vector3') -> float:
        return self.x*other.x + self.y*other.y + self.z*other.z

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)

    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x*scalar, self.y*scalar, self.z*scalar)


@dataclass
class Force:
    """A force acting on an object."""
    force_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    direction: Vector3 = field(default_factory=Vector3)
    magnitude: float = 0.0
    duration: float = 0.0  # seconds (0 = instant)
    source: str = ""  # object applying force
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_vector(self) -> Vector3:
        """Get force as vector."""
        normalized = self.direction.normalize()
        return normalized * self.magnitude


@dataclass
class PhysicsObject:
    """A physics-enabled object in the world."""
    object_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    obj_type: PhysicsObjectType = PhysicsObjectType.RIGID_BODY
    mass: float = 1.0
    position: Vector3 = field(default_factory=Vector3)
    velocity: Vector3 = field(default_factory=Vector3)
    acceleration: Vector3 = field(default_factory=Vector3)
    forces: List[Force] = field(default_factory=list)
    friction: float = 0.1
    elasticity: float = 0.8
    radius: float = 1.0  # For collision detection
    kinetic_energy: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def apply_force(self, force: Force) -> None:
        """Apply a force to this object."""
        self.forces.append(force)

    def update_acceleration(self) -> None:
        """Calculate acceleration from all forces."""
        net_force = Vector3()
        for force in self.forces:
            net_force = net_force + force.get_vector()
        # F = ma, so a = F/m
        self.acceleration = net_force * (1.0 / self.mass)

    def update_velocity(self, dt: float) -> None:
        """Update velocity based on acceleration."""
        self.velocity = self.velocity + (self.acceleration * dt)
        # Apply friction
        self.velocity = self.velocity * (1.0 - self.friction * dt)

    def update_position(self, dt: float) -> None:
        """Update position based on velocity."""
        self.position = self.position + (self.velocity * dt)

    def calculate_kinetic_energy(self) -> float:
        """Calculate kinetic energy: KE = 0.5 * m * v^2."""
        v_squared = self.velocity.dot(self.velocity)
        return 0.5 * self.mass * v_squared

    def step_physics(self, dt: float) -> None:
        """Perform one physics step."""
        self.update_acceleration()
        self.update_velocity(dt)
        self.update_position(dt)
        self.kinetic_energy = self.calculate_kinetic_energy()
        # Remove expired forces
        self.forces = [
            f for f in self.forces
            if (datetime.utcnow() - f.created_at).total_seconds() < f.duration or f.duration == 0
        ]


class PhysicsEngine:
    """Main physics simulation engine."""

    def __init__(self, gravity: Vector3 = None, dt: float = 0.016):
        self.objects: Dict[str, PhysicsObject] = {}
        self.gravity = gravity or Vector3(0, -9.81, 0)
        self.dt = dt  # Timestep in seconds
        self.time: float = 0.0
        self.collisions: List[Tuple[str, str]] = []

    def add_object(self, obj: PhysicsObject) -> str:
        """Add an object to the physics simulation."""
        self.objects[obj.object_id] = obj
        # Apply gravity
        gravity_force = Force(
            direction=self.gravity.normalize(),
            magnitude=self.gravity.magnitude() * obj.mass,
            duration=0,  # Permanent
            source="world_gravity",
        )
        obj.apply_force(gravity_force)
        return obj.object_id

    def remove_object(self, object_id: str) -> bool:
        """Remove an object from the simulation."""
        if object_id in self.objects:
            del self.objects[object_id]
            return True
        return False

    def get_object(self, object_id: str) -> Optional[PhysicsObject]:
        """Get a physics object."""
        return self.objects.get(object_id)

    def step(self) -> None:
        """Execute one physics simulation step."""
        # Update all objects
        for obj in self.objects.values():
            obj.step_physics(self.dt)

        # Detect collisions
        self._detect_collisions()
        self.time += self.dt

    def _detect_collisions(self) -> None:
        """Detect collisions between objects."""
        self.collisions = []
        objects_list = list(self.objects.values())

        for i, obj1 in enumerate(objects_list):
            for obj2 in objects_list[i+1:]:
                if self._check_collision(obj1, obj2):
                    self.collisions.append((obj1.object_id, obj2.object_id))
                    self._resolve_collision(obj1, obj2)

    def _check_collision(self, obj1: PhysicsObject, obj2: PhysicsObject) -> bool:
        """Check if two objects collide using distance formula."""
        dx = obj2.position.x - obj1.position.x
        dy = obj2.position.y - obj1.position.y
        dz = obj2.position.z - obj1.position.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        return distance < (obj1.radius + obj2.radius)

    def _resolve_collision(self, obj1: PhysicsObject, obj2: PhysicsObject) -> None:
        """Resolve collision between two objects (elastic collision)."""
        # Simplified elastic collision resolution
        m1, m2 = obj1.mass, obj2.mass
        v1, v2 = obj1.velocity, obj2.velocity

        # Exchange velocities based on masses
        new_v1 = (v1 * (m1 - m2) + v2 * 2 * m2) * (1 / (m1 + m2))
        new_v2 = (v2 * (m2 - m1) + v1 * 2 * m1) * (1 / (m1 + m2))

        obj1.velocity = new_v1
        obj2.velocity = new_v2

        # Apply damping
        obj1.velocity = obj1.velocity * obj1.elasticity
        obj2.velocity = obj2.velocity * obj2.elasticity

    def get_state(self) -> Dict[str, Any]:
        """Get current physics engine state."""
        return {
            'time': self.time,
            'total_objects': len(self.objects),
            'recent_collisions': len(self.collisions),
            'total_kinetic_energy': sum(obj.kinetic_energy for obj in self.objects.values()),
        }
