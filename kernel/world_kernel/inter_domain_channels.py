"""Inter-Domain Channels - Cross-Domain Communication

Implements communication channels for message passing between domains
with flow control, ordering guarantees, and reliability.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Deque
from enum import Enum
from collections import deque
import uuid
from datetime import datetime
import heapq


class MessageType(Enum):
    """Types of messages sent through channels."""
    STATE_UPDATE = "state_update"
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"
    ACK = "ack"
    NACK = "nack"
    HEARTBEAT = "heartbeat"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"


class MessagePriority(Enum):
    """Priority levels for message delivery."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class ChannelMode(Enum):
    """Communication modes for channels."""
    SYNC = "sync"  # Blocking call-response
    ASYNC = "async"  # Non-blocking with callback
    STREAM = "stream"  # Continuous stream
    BROADCAST = "broadcast"  # One-to-many


@dataclass
class Message:
    """A message sent through an inter-domain channel."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.STATE_UPDATE
    sender_domain: str = ""
    receiver_domain: str = ""
    payload: Any = None
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence_number: int = 0  # For ordering
    requires_ack: bool = True
    ack_received: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: 'Message') -> bool:
        """Compare messages by priority and sequence."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.sequence_number < other.sequence_number


@dataclass
class ChannelStatistics:
    """Statistics for a channel."""
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_acks_received: int = 0
    total_messages_dropped: int = 0
    average_latency_ms: float = 0.0
    capacity: int = 1000
    current_buffer_size: int = 0
    error_count: int = 0


class InterDomainChannel:
    """A communication channel between two domains."""

    def __init__(
        self,
        channel_id: str,
        source_domain: str,
        destination_domain: str,
        mode: ChannelMode = ChannelMode.ASYNC,
        capacity: int = 1000,
    ):
        self.channel_id = channel_id
        self.source_domain = source_domain
        self.destination_domain = destination_domain
        self.mode = mode
        self.capacity = capacity

        # Message queues
        self.outbound_queue: Deque[Message] = deque()
        self.inbound_queue: Deque[Message] = deque()
        self.priority_queue: List[Message] = []  # Heap for priority messages

        # Tracking
        self.statistics = ChannelStatistics(capacity=capacity)
        self.pending_acks: Dict[str, Message] = {}  # message_id -> message
        self.message_history: List[Message] = []
        self.callbacks: Dict[str, List[Callable]] = {
            'message_received': [],
            'ack_received': [],
            'error': [],
        }

        # Flow control
        self.backpressure_enabled = False
        self.max_in_flight = 100
        self.in_flight_messages: Dict[str, float] = {}  # message_id -> send_time

    def send_message(
        self,
        message_type: MessageType,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = True,
    ) -> Optional[str]:
        """Send a message through the channel."""
        # Check backpressure
        if self.backpressure_enabled and len(self.in_flight_messages) >= self.max_in_flight:
            self.statistics.total_messages_dropped += 1
            return None

        # Check buffer capacity
        if len(self.outbound_queue) >= self.capacity:
            self.statistics.total_messages_dropped += 1
            return None

        message = Message(
            message_type=message_type,
            sender_domain=self.source_domain,
            receiver_domain=self.destination_domain,
            payload=payload,
            priority=priority,
            requires_ack=requires_ack,
            sequence_number=self.statistics.total_messages_sent,
        )

        # Add to queue based on priority
        if priority == MessagePriority.CRITICAL:
            # Use priority heap
            heapq.heappush(self.priority_queue, message)
        else:
            self.outbound_queue.append(message)

        if requires_ack:
            self.pending_acks[message.message_id] = message
            self.in_flight_messages[message.message_id] = datetime.utcnow().timestamp()

        self.statistics.total_messages_sent += 1
        self.message_history.append(message)
        return message.message_id

    def receive_message(self) -> Optional[Message]:
        """Receive a message from the channel."""
        if not self.inbound_queue:
            return None

        message = self.inbound_queue.popleft()
        self.statistics.total_messages_received += 1

        # Trigger callbacks
        for callback in self.callbacks['message_received']:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in message callback: {e}")
                self.statistics.error_count += 1

        return message

    def acknowledge_message(self, message_id: str) -> bool:
        """Send acknowledgment for a received message."""
        if message_id not in self.pending_acks:
            return False

        message = self.pending_acks[message_id]
        message.ack_received = True
        self.statistics.total_acks_received += 1

        # Remove from in-flight tracking
        if message_id in self.in_flight_messages:
            send_time = self.in_flight_messages[message_id]
            latency = (datetime.utcnow().timestamp() - send_time) * 1000  # ms
            # Update average latency
            old_avg = self.statistics.average_latency_ms
            old_count = self.statistics.total_acks_received - 1
            self.statistics.average_latency_ms = (
                (old_avg * old_count + latency) / self.statistics.total_acks_received
            )
            del self.in_flight_messages[message_id]

        del self.pending_acks[message_id]

        # Trigger callbacks
        for callback in self.callbacks['ack_received']:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in ack callback: {e}")

        return True

    def flush_outbound(self) -> List[Message]:
        """Get all messages ready to send."""
        messages = []

        # Priority messages first
        while self.priority_queue and len(messages) < self.capacity:
            messages.append(heapq.heappop(self.priority_queue))

        # Regular messages
        while self.outbound_queue and len(messages) < self.capacity:
            messages.append(self.outbound_queue.popleft())

        return messages

    def inject_inbound(self, message: Message):
        """Inject a message into the inbound queue (receive)."""
        if len(self.inbound_queue) >= self.capacity:
            self.statistics.total_messages_dropped += 1
            return

        self.inbound_queue.append(message)
        self.statistics.current_buffer_size = len(self.inbound_queue)

    def get_statistics(self) -> Dict[str, Any]:
        """Get channel statistics."""
        return {
            'total_messages_sent': self.statistics.total_messages_sent,
            'total_messages_received': self.statistics.total_messages_received,
            'total_acks_received': self.statistics.total_acks_received,
            'total_messages_dropped': self.statistics.total_messages_dropped,
            'average_latency_ms': self.statistics.average_latency_ms,
            'current_buffer_size': self.statistics.current_buffer_size,
            'capacity': self.statistics.capacity,
            'pending_acks': len(self.pending_acks),
            'error_count': self.statistics.error_count,
        }


class ChannelMesh:
    """Mesh of inter-domain channels."""

    def __init__(self):
        self.channels: Dict[str, InterDomainChannel] = {}
        self.domain_pairs: Dict[str, str] = {}  # (src,dst) -> channel_id

    def create_channel(
        self,
        source_domain: str,
        destination_domain: str,
        mode: ChannelMode = ChannelMode.ASYNC,
        capacity: int = 1000,
    ) -> str:
        """Create a new communication channel."""
        channel_id = f"{source_domain}→{destination_domain}"
        channel = InterDomainChannel(
            channel_id=channel_id,
            source_domain=source_domain,
            destination_domain=destination_domain,
            mode=mode,
            capacity=capacity,
        )
        self.channels[channel_id] = channel
        self.domain_pairs[(source_domain, destination_domain)] = channel_id
        return channel_id

    def get_channel(
        self,
        source_domain: str,
        destination_domain: str,
    ) -> Optional[InterDomainChannel]:
        """Get a channel between two domains."""
        channel_id = self.domain_pairs.get((source_domain, destination_domain))
        if channel_id:
            return self.channels.get(channel_id)
        return None

    def broadcast_message(
        self,
        source_domain: str,
        destinations: List[str],
        message_type: MessageType,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> List[str]:
        """Broadcast a message to multiple destinations."""
        message_ids = []
        for dest in destinations:
            channel = self.get_channel(source_domain, dest)
            if channel:
                msg_id = channel.send_message(
                    message_type,
                    payload,
                    priority,
                )
                if msg_id:
                    message_ids.append(msg_id)
        return message_ids

    def get_mesh_health(self) -> Dict[str, Any]:
        """Get overall health of the channel mesh."""
        total_messages = sum(c.statistics.total_messages_sent for c in self.channels.values())
        total_dropped = sum(c.statistics.total_messages_dropped for c in self.channels.values())
        total_errors = sum(c.statistics.error_count for c in self.channels.values())
        avg_latency = (
            sum(c.statistics.average_latency_ms for c in self.channels.values())
            / len(self.channels)
            if self.channels else 0
        )

        return {
            'total_channels': len(self.channels),
            'total_messages_sent': total_messages,
            'total_messages_dropped': total_dropped,
            'drop_rate_percentage': (total_dropped / total_messages * 100) if total_messages > 0 else 0,
            'average_latency_ms': avg_latency,
            'total_errors': total_errors,
        }
