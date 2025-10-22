"""
Event Store for CRDT State Persistence

Implements event sourcing pattern with PostgreSQL backend.
Stores all state changes as immutable events for audit trail and recovery.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class Event:
    """
    Represents a single event in the event store.
    
    Attributes:
        event_id: Unique identifier for the event
        entity_id: ID of the entity this event applies to
        event_type: Type of event (e.g., 'file_created', 'file_updated')
        data: Event payload data
        timestamp: When the event occurred
        node_id: Node that generated the event
        vector_clock: Serialized vector clock state
    """
    
    def __init__(self, entity_id: str, event_type: str, data: Dict[str, Any],
                 node_id: str, vector_clock: Dict[str, int],
                 event_id: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        """
        Initialize an event.
        
        Args:
            entity_id: ID of entity (e.g., file_id, user_id)
            event_type: Type of event
            data: Event payload
            node_id: Node that generated the event
            vector_clock: Vector clock state as dict
            event_id: Optional event ID (generated if not provided)
            timestamp: Optional timestamp (current time if not provided)
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.entity_id = entity_id
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.node_id = node_id
        self.vector_clock = vector_clock
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'entity_id': self.entity_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'node_id': self.node_id,
            'vector_clock': self.vector_clock
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data['event_id'],
            entity_id=data['entity_id'],
            event_type=data['event_type'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
            node_id=data['node_id'],
            vector_clock=data['vector_clock']
        )
    
    def __repr__(self) -> str:
        return f"Event(id={self.event_id}, type={self.event_type}, entity={self.entity_id})"


class EventStore:
    """
    Event Store for persisting CRDT events to PostgreSQL.
    
    Provides event sourcing capabilities with:
    - Append-only event log
    - Event replay for state reconstruction
    - Snapshot support for performance
    - Query by entity, time range, or event type
    """
    
    def __init__(self, db_manager):
        """
        Initialize event store.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        logger.info("EventStore initialized")
    
    def append_event(self, event: Event) -> bool:
        """
        Append a new event to the store.
        
        Args:
            event: Event to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
            INSERT INTO crdt_events (
                event_id, entity_id, event_type, data, 
                timestamp, node_id, vector_clock
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                event.event_id,
                event.entity_id,
                event.event_type,
                json.dumps(event.data),
                event.timestamp,
                event.node_id,
                json.dumps(event.vector_clock)
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Appended event: {event}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append event: {e}", exc_info=True)
            return False
    
    def get_events(self, entity_id: str, 
                   since: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[Event]:
        """
        Get events for a specific entity.
        
        Args:
            entity_id: Entity ID to query
            since: Optional timestamp to get events after
            limit: Optional maximum number of events to return
            
        Returns:
            List of Event objects ordered by timestamp
        """
        try:
            query = """
            SELECT event_id, entity_id, event_type, data, 
                   timestamp, node_id, vector_clock
            FROM crdt_events
            WHERE entity_id = %s
            """
            params = [entity_id]
            
            if since:
                query += " AND timestamp > %s"
                params.append(since)
            
            query += " ORDER BY timestamp ASC"
            
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            rows = self.db.execute_query(query, tuple(params))
            
            events = []
            for row in rows:
                event = Event(
                    event_id=row['event_id'],
                    entity_id=row['entity_id'],
                    event_type=row['event_type'],
                    data=json.loads(row['data']) if isinstance(row['data'], str) else row['data'],
                    timestamp=row['timestamp'],
                    node_id=row['node_id'],
                    vector_clock=json.loads(row['vector_clock']) if isinstance(row['vector_clock'], str) else row['vector_clock']
                )
                events.append(event)
            
            logger.debug(f"Retrieved {len(events)} events for entity {entity_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}", exc_info=True)
            return []
    
    def get_all_events(self, since: Optional[datetime] = None,
                       limit: Optional[int] = 1000) -> List[Event]:
        """
        Get all events across all entities.
        
        Args:
            since: Optional timestamp to get events after
            limit: Maximum number of events (default 1000)
            
        Returns:
            List of Event objects ordered by timestamp
        """
        try:
            query = """
            SELECT event_id, entity_id, event_type, data,
                   timestamp, node_id, vector_clock
            FROM crdt_events
            """
            params = []
            
            if since:
                query += " WHERE timestamp > %s"
                params.append(since)
            
            query += " ORDER BY timestamp ASC LIMIT %s"
            params.append(limit)
            
            rows = self.db.execute_query(query, tuple(params) if params else None)
            
            events = []
            for row in rows:
                event = Event(
                    event_id=row['event_id'],
                    entity_id=row['entity_id'],
                    event_type=row['event_type'],
                    data=json.loads(row['data']) if isinstance(row['data'], str) else row['data'],
                    timestamp=row['timestamp'],
                    node_id=row['node_id'],
                    vector_clock=json.loads(row['vector_clock']) if isinstance(row['vector_clock'], str) else row['vector_clock']
                )
                events.append(event)
            
            logger.debug(f"Retrieved {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get all events: {e}", exc_info=True)
            return []
    
    def save_snapshot(self, entity_id: str, state: Dict[str, Any],
                     vector_clock: Dict[str, int]) -> bool:
        """
        Save a state snapshot for fast recovery.
        
        Args:
            entity_id: Entity ID
            state: Current state to snapshot
            vector_clock: Current vector clock state
            
        Returns:
            True if successful
        """
        try:
            query = """
            INSERT INTO crdt_snapshots (entity_id, state, vector_clock, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (entity_id) 
            DO UPDATE SET 
                state = EXCLUDED.state,
                vector_clock = EXCLUDED.vector_clock,
                created_at = EXCLUDED.created_at
            """
            
            params = (
                entity_id,
                json.dumps(state),
                json.dumps(vector_clock),
                datetime.utcnow()
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Saved snapshot for entity {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}", exc_info=True)
            return False
    
    def get_snapshot(self, entity_id: str) -> Optional[Tuple[Dict[str, Any], Dict[str, int], datetime]]:
        """
        Get the latest snapshot for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Tuple of (state, vector_clock, timestamp) or None
        """
        try:
            query = """
            SELECT state, vector_clock, created_at
            FROM crdt_snapshots
            WHERE entity_id = %s
            """
            
            rows = self.db.execute_query(query, (entity_id,))
            
            if rows:
                row = rows[0]
                state = json.loads(row['state']) if isinstance(row['state'], str) else row['state']
                vector_clock = json.loads(row['vector_clock']) if isinstance(row['vector_clock'], str) else row['vector_clock']
                return (state, vector_clock, row['created_at'])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get snapshot: {e}", exc_info=True)
            return None
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Event]:
        """
        Get events by type.
        
        Args:
            event_type: Type of events to retrieve
            limit: Maximum number of events
            
        Returns:
            List of Event objects
        """
        try:
            query = """
            SELECT event_id, entity_id, event_type, data,
                   timestamp, node_id, vector_clock
            FROM crdt_events
            WHERE event_type = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """
            
            rows = self.db.execute_query(query, (event_type, limit))
            
            events = []
            for row in rows:
                event = Event(
                    event_id=row['event_id'],
                    entity_id=row['entity_id'],
                    event_type=row['event_type'],
                    data=json.loads(row['data']) if isinstance(row['data'], str) else row['data'],
                    timestamp=row['timestamp'],
                    node_id=row['node_id'],
                    vector_clock=json.loads(row['vector_clock']) if isinstance(row['vector_clock'], str) else row['vector_clock']
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events by type: {e}", exc_info=True)
            return []
