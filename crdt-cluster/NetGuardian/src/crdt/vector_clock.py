"""
Vector Clock Implementation for CRDT
Tracks causality in distributed systems to ensure proper event ordering
"""

from typing import Dict, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class VectorClock:
    """
    Vector Clock for tracking causality in distributed systems.
    
    Each node maintains a counter for every node in the system.
    Used to determine if events are concurrent or causally related.
    
    Attributes:
        node_id: Unique identifier for this node/device
        clock: Dictionary mapping node_id to counter value
    """
    
    def __init__(self, node_id: str, clock: Optional[Dict[str, int]] = None):
        """
        Initialize a vector clock.
        
        Args:
            node_id: Unique identifier for this node
            clock: Optional initial clock state
        """
        self.node_id = node_id
        self.clock: Dict[str, int] = clock if clock is not None else {node_id: 0}
    
    def increment(self) -> None:
        """Increment this node's counter."""
        if self.node_id not in self.clock:
            self.clock[self.node_id] = 0
        self.clock[self.node_id] += 1
        logger.debug(f"Incremented clock for {self.node_id}: {self.clock}")
    
    def update(self, other: 'VectorClock') -> None:
        """
        Update this clock by taking the maximum of each component.
        
        Args:
            other: Another vector clock to merge with
        """
        for node_id, value in other.clock.items():
            self.clock[node_id] = max(self.clock.get(node_id, 0), value)
        logger.debug(f"Updated clock: {self.clock}")
    
    def compare(self, other: 'VectorClock') -> str:
        """
        Compare two vector clocks to determine causal relationship.
        
        Args:
            other: Vector clock to compare with
            
        Returns:
            'before': self happened before other
            'after': self happened after other
            'concurrent': events are concurrent
            'equal': clocks are identical
        """
        all_nodes = set(self.clock.keys()) | set(other.clock.keys())
        
        self_less = False
        self_greater = False
        
        for node in all_nodes:
            self_val = self.clock.get(node, 0)
            other_val = other.clock.get(node, 0)
            
            if self_val < other_val:
                self_less = True
            elif self_val > other_val:
                self_greater = True
        
        if not self_less and not self_greater:
            return 'equal'
        elif self_less and not self_greater:
            return 'before'
        elif self_greater and not self_less:
            return 'after'
        else:
            return 'concurrent'
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """
        Check if this clock happens before another clock.
        
        Args:
            other: Vector clock to compare with
            
        Returns:
            True if self <= other and self != other
        """
        return self.compare(other) == 'before'
    
    def is_concurrent(self, other: 'VectorClock') -> bool:
        """
        Check if two clocks are concurrent (no causal relationship).
        
        Args:
            other: Vector clock to compare with
            
        Returns:
            True if events are concurrent
        """
        return self.compare(other) == 'concurrent'
    
    def copy(self) -> 'VectorClock':
        """Create a deep copy of this vector clock."""
        return VectorClock(self.node_id, self.clock.copy())
    
    def to_dict(self) -> Dict:
        """
        Serialize vector clock to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'node_id': self.node_id,
            'clock': self.clock
        }
    
    def to_json(self) -> str:
        """
        Serialize vector clock to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VectorClock':
        """
        Deserialize vector clock from dictionary.
        
        Args:
            data: Dictionary containing node_id and clock
            
        Returns:
            VectorClock instance
        """
        return cls(data['node_id'], data['clock'])
    
    @classmethod
    def from_json(cls, json_str: str) -> 'VectorClock':
        """
        Deserialize vector clock from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            VectorClock instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of vector clock."""
        return f"VectorClock({self.node_id}: {self.clock})"
    
    def __repr__(self) -> str:
        """Detailed representation of vector clock."""
        return f"VectorClock(node_id='{self.node_id}', clock={self.clock})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another vector clock."""
        if not isinstance(other, VectorClock):
            return False
        return self.compare(other) == 'equal'
    
    def __lt__(self, other) -> bool:
        """Check if this clock is less than (happens before) another."""
        return self.happens_before(other)
