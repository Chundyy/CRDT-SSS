"""
Last-Write-Wins Register (LWW-Register) CRDT Implementation

State-based CRDT that resolves conflicts using timestamps and node IDs.
Guarantees eventual consistency in distributed file systems.
"""

from typing import Any, Optional, Dict, Tuple
from datetime import datetime
import json
import logging
from .vector_clock import VectorClock

logger = logging.getLogger(__name__)


class LWWRegister:
    """
    Last-Write-Wins Register - A state-based CRDT.
    
    Resolves conflicts by choosing the value with the latest timestamp.
    In case of timestamp ties, uses node_id for deterministic ordering.
    
    Attributes:
        value: Current value stored in the register
        timestamp: Timestamp of last write
        node_id: ID of the node that performed the last write
        vector_clock: Vector clock for causality tracking
    """
    
    def __init__(self, node_id: str, value: Any = None, 
                 timestamp: Optional[datetime] = None,
                 vector_clock: Optional[VectorClock] = None):
        """
        Initialize LWW-Register.
        
        Args:
            node_id: Unique identifier for this node
            value: Initial value
            timestamp: Initial timestamp (defaults to current time)
            vector_clock: Optional vector clock for causality
        """
        self.node_id = node_id
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()
        self.vector_clock = vector_clock or VectorClock(node_id)
        logger.debug(f"Created LWWRegister: {self}")
    
    def set(self, value: Any) -> None:
        """
        Set a new value in the register.
        
        Args:
            value: New value to store
        """
        self.value = value
        self.timestamp = datetime.utcnow()
        self.vector_clock.increment()
        logger.info(f"LWWRegister updated: value={value}, timestamp={self.timestamp}")
    
    def get(self) -> Any:
        """
        Get the current value from the register.
        
        Returns:
            Current value
        """
        return self.value
    
    def merge(self, other: 'LWWRegister') -> None:
        """
        Merge this register with another LWW-Register.
        
        Takes the value with the latest timestamp. In case of tie,
        uses lexicographic ordering of node_id for determinism.
        
        Args:
            other: Another LWWRegister to merge with
        """
        logger.debug(f"Merging registers: {self} with {other}")
        
        # Compare timestamps
        if other.timestamp > self.timestamp:
            # Other is newer
            self.value = other.value
            self.timestamp = other.timestamp
            self.node_id = other.node_id
            logger.info(f"Merged: adopted other's value (newer timestamp)")
        elif other.timestamp == self.timestamp:
            # Timestamp tie - use node_id for deterministic ordering
            if other.node_id > self.node_id:
                self.value = other.value
                self.node_id = other.node_id
                logger.info(f"Merged: adopted other's value (tie-break by node_id)")
        else:
            # Self is newer - keep current value
            logger.info(f"Merged: kept current value (newer timestamp)")
        
        # Update vector clock
        self.vector_clock.update(other.vector_clock)
    
    def is_concurrent(self, other: 'LWWRegister') -> bool:
        """
        Check if two registers have concurrent updates.
        
        Args:
            other: Another LWWRegister to compare
            
        Returns:
            True if updates are concurrent
        """
        return self.vector_clock.is_concurrent(other.vector_clock)
    
    def copy(self) -> 'LWWRegister':
        """
        Create a deep copy of this register.
        
        Returns:
            New LWWRegister instance with copied values
        """
        return LWWRegister(
            node_id=self.node_id,
            value=self.value,
            timestamp=self.timestamp,
            vector_clock=self.vector_clock.copy()
        )
    
    def to_dict(self) -> Dict:
        """
        Serialize register to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'node_id': self.node_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'vector_clock': self.vector_clock.to_dict()
        }
    
    def to_json(self) -> str:
        """
        Serialize register to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LWWRegister':
        """
        Deserialize register from dictionary.
        
        Args:
            data: Dictionary containing register data
            
        Returns:
            LWWRegister instance
        """
        return cls(
            node_id=data['node_id'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            vector_clock=VectorClock.from_dict(data['vector_clock'])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LWWRegister':
        """
        Deserialize register from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            LWWRegister instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of register."""
        return f"LWWRegister(value={self.value}, ts={self.timestamp}, node={self.node_id})"
    
    def __repr__(self) -> str:
        """Detailed representation of register."""
        return (f"LWWRegister(node_id='{self.node_id}', value={self.value}, "
                f"timestamp={self.timestamp}, vector_clock={self.vector_clock})")
    
    def __eq__(self, other) -> bool:
        """Check equality with another register."""
        if not isinstance(other, LWWRegister):
            return False
        return (self.value == other.value and 
                self.timestamp == other.timestamp and
                self.node_id == other.node_id)
