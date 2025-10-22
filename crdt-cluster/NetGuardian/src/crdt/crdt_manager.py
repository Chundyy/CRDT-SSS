"""
CRDT Manager for NetGuardian

Manages CRDT states for distributed file operations with automatic conflict resolution.
Coordinates between event store, vector clocks, and LWW registers.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging
import json

from .vector_clock import VectorClock
from .lww_register import LWWRegister
from .event_store import EventStore, Event

logger = logging.getLogger(__name__)


class CRDTManager:
    """
    Central manager for CRDT operations in NetGuardian.
    
    Provides high-level API for:
    - Creating and updating file states with CRDTs
    - Automatic conflict resolution
    - State synchronization across nodes
    - Event sourcing for audit trail
    
    Attributes:
        node_id: Unique identifier for this node/device
        event_store: EventStore instance for persistence
        registers: Cache of active LWW registers by entity_id
    """
    
    def __init__(self, db_manager, node_id: Optional[str] = None):
        """
        Initialize CRDT Manager.
        
        Args:
            db_manager: Database manager instance
            node_id: Optional node ID (generated if not provided)
        """
        self.node_id = node_id or self._generate_node_id()
        self.event_store = EventStore(db_manager)
        self.registers: Dict[str, LWWRegister] = {}
        self.db = db_manager
        logger.info(f"CRDTManager initialized with node_id: {self.node_id}")
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        import platform
        hostname = platform.node()
        unique_id = str(uuid.uuid4())[:8]
        return f"{hostname}-{unique_id}"
    
    def create_file_state(self, file_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Create a new file state with CRDT.
        
        Args:
            file_id: Unique file identifier
            metadata: File metadata (name, size, path, etc.)
            
        Returns:
            True if successful
        """
        try:
            # Create LWW register for this file
            register = LWWRegister(self.node_id, value=metadata)
            self.registers[file_id] = register
            
            # Create event
            event = Event(
                entity_id=file_id,
                event_type='file_created',
                data={
                    'metadata': metadata,
                    'operation': 'create'
                },
                node_id=self.node_id,
                vector_clock=register.vector_clock.clock
            )
            
            # Persist event
            success = self.event_store.append_event(event)
            
            if success:
                # Save current state
                self._save_current_state(file_id, register)
                logger.info(f"Created file state for {file_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create file state: {e}", exc_info=True)
            return False
    
    def update_file_state(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update file state with CRDT merge.
        
        Args:
            file_id: File identifier
            updates: Updated metadata fields
            
        Returns:
            True if successful
        """
        try:
            # Get or create register
            register = self._get_or_load_register(file_id)
            
            if register is None:
                logger.warning(f"File {file_id} not found, creating new state")
                return self.create_file_state(file_id, updates)
            
            # Merge updates with existing metadata
            current_value = register.get() or {}
            new_value = {**current_value, **updates}
            
            # Update register
            register.set(new_value)
            self.registers[file_id] = register
            
            # Create event
            event = Event(
                entity_id=file_id,
                event_type='file_updated',
                data={
                    'updates': updates,
                    'full_state': new_value,
                    'operation': 'update'
                },
                node_id=self.node_id,
                vector_clock=register.vector_clock.clock
            )
            
            # Persist event
            success = self.event_store.append_event(event)
            
            if success:
                self._save_current_state(file_id, register)
                logger.info(f"Updated file state for {file_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update file state: {e}", exc_info=True)
            return False
    
    def delete_file_state(self, file_id: str) -> bool:
        """
        Mark file as deleted (tombstone).
        
        Args:
            file_id: File identifier
            
        Returns:
            True if successful
        """
        try:
            register = self._get_or_load_register(file_id)
            
            if register is None:
                logger.warning(f"File {file_id} not found for deletion")
                return False
            
            # Set tombstone
            current_value = register.get() or {}
            current_value['deleted'] = True
            current_value['deleted_at'] = datetime.utcnow().isoformat()
            
            register.set(current_value)
            self.registers[file_id] = register
            
            # Create event
            event = Event(
                entity_id=file_id,
                event_type='file_deleted',
                data={
                    'operation': 'delete',
                    'deleted_at': current_value['deleted_at']
                },
                node_id=self.node_id,
                vector_clock=register.vector_clock.clock
            )
            
            success = self.event_store.append_event(event)
            
            if success:
                self._save_current_state(file_id, register)
                logger.info(f"Deleted file state for {file_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete file state: {e}", exc_info=True)
            return False
    
    def get_file_state(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current file state.
        
        Args:
            file_id: File identifier
            
        Returns:
            File metadata dict or None
        """
        try:
            register = self._get_or_load_register(file_id)
            
            if register is None:
                return None
            
            return register.get()
            
        except Exception as e:
            logger.error(f"Failed to get file state: {e}", exc_info=True)
            return None
    
    def sync_from_remote(self, remote_events: List[Event]) -> int:
        """
        Synchronize with remote events (for multi-device sync).
        
        Args:
            remote_events: List of events from remote node
            
        Returns:
            Number of events merged
        """
        merged_count = 0
        
        try:
            for event in remote_events:
                # Load local register
                local_register = self._get_or_load_register(event.entity_id)
                
                # Create remote register from event
                remote_register = LWWRegister(
                    node_id=event.node_id,
                    value=event.data.get('full_state') or event.data.get('metadata'),
                    timestamp=event.timestamp,
                    vector_clock=VectorClock.from_dict({
                        'node_id': event.node_id,
                        'clock': event.vector_clock
                    })
                )
                
                if local_register is None:
                    # New file from remote
                    self.registers[event.entity_id] = remote_register
                    self.event_store.append_event(event)
                    self._save_current_state(event.entity_id, remote_register)
                    merged_count += 1
                else:
                    # Merge with existing
                    local_register.merge(remote_register)
                    self.registers[event.entity_id] = local_register
                    self.event_store.append_event(event)
                    self._save_current_state(event.entity_id, local_register)
                    merged_count += 1
                
                logger.debug(f"Merged event for {event.entity_id}")
            
            logger.info(f"Synced {merged_count} events from remote")
            return merged_count
            
        except Exception as e:
            logger.error(f"Failed to sync from remote: {e}", exc_info=True)
            return merged_count
    
    def get_changes_since(self, since: datetime) -> List[Event]:
        """
        Get all changes since a given timestamp (for sync).
        
        Args:
            since: Timestamp to get changes after
            
        Returns:
            List of events
        """
        return self.event_store.get_all_events(since=since)
    
    def rebuild_state_from_events(self, file_id: str) -> Optional[LWWRegister]:
        """
        Rebuild state by replaying events (event sourcing).
        
        Args:
            file_id: File identifier
            
        Returns:
            Rebuilt LWWRegister or None
        """
        try:
            events = self.event_store.get_events(file_id)
            
            if not events:
                return None
            
            # Start with first event
            first_event = events[0]
            register = LWWRegister(
                node_id=first_event.node_id,
                value=first_event.data.get('metadata') or first_event.data.get('full_state'),
                timestamp=first_event.timestamp,
                vector_clock=VectorClock.from_dict({
                    'node_id': first_event.node_id,
                    'clock': first_event.vector_clock
                })
            )
            
            # Replay remaining events
            for event in events[1:]:
                remote_register = LWWRegister(
                    node_id=event.node_id,
                    value=event.data.get('full_state') or event.data.get('updates'),
                    timestamp=event.timestamp,
                    vector_clock=VectorClock.from_dict({
                        'node_id': event.node_id,
                        'clock': event.vector_clock
                    })
                )
                register.merge(remote_register)
            
            logger.info(f"Rebuilt state for {file_id} from {len(events)} events")
            return register
            
        except Exception as e:
            logger.error(f"Failed to rebuild state: {e}", exc_info=True)
            return None
    
    def _get_or_load_register(self, file_id: str) -> Optional[LWWRegister]:
        """Get register from cache or load from database."""
        # Check cache
        if file_id in self.registers:
            return self.registers[file_id]
        
        # Try to load from snapshot
        snapshot = self.event_store.get_snapshot(file_id)
        if snapshot:
            state, vector_clock_dict, _ = snapshot
            register = LWWRegister(
                node_id=self.node_id,
                value=state,
                vector_clock=VectorClock.from_dict({
                    'node_id': self.node_id,
                    'clock': vector_clock_dict
                })
            )
            self.registers[file_id] = register
            return register
        
        # Rebuild from events
        register = self.rebuild_state_from_events(file_id)
        if register:
            self.registers[file_id] = register
        
        return register
    
    def _save_current_state(self, file_id: str, register: LWWRegister) -> None:
        """Save current state as snapshot."""
        try:
            self.event_store.save_snapshot(
                entity_id=file_id,
                state=register.get(),
                vector_clock=register.vector_clock.clock
            )
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get CRDT system statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            return {
                'node_id': self.node_id,
                'active_registers': len(self.registers),
                'total_entities': len(self.registers)
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
