"""
Sync Engine for CRDT State Synchronization

Manages synchronization between local and remote CRDT states.
Supports pull, push, and bidirectional sync strategies.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .event_store import Event
from .crdt_manager import CRDTManager

logger = logging.getLogger(__name__)


class SyncEngine:
    """
    Synchronization engine for CRDT states.
    
    Coordinates state synchronization between nodes with:
    - Pull sync: Get updates from remote
    - Push sync: Send updates to remote
    - Bidirectional sync: Exchange updates
    - Conflict-free merge using CRDT properties
    
    Attributes:
        crdt_manager: CRDTManager instance
        db: Database manager
        node_id: This node's identifier
        last_sync: Timestamp of last successful sync
    """
    
    def __init__(self, crdt_manager: CRDTManager):
        """
        Initialize sync engine.
        
        Args:
            crdt_manager: CRDTManager instance to coordinate
        """
        self.crdt_manager = crdt_manager
        self.db = crdt_manager.db
        self.node_id = crdt_manager.node_id
        self.last_sync: Optional[datetime] = None
        logger.info(f"SyncEngine initialized for node {self.node_id}")
    
    def pull_sync(self, remote_events: List[Event]) -> Dict[str, Any]:
        """
        Pull and merge remote events into local state.
        
        Args:
            remote_events: List of events from remote node
            
        Returns:
            Sync result with statistics
        """
        try:
            start_time = datetime.utcnow()
            
            if not remote_events:
                logger.info("No remote events to sync")
                return {
                    'success': True,
                    'events_merged': 0,
                    'duration_ms': 0
                }
            
            # Merge remote events
            merged_count = self.crdt_manager.sync_from_remote(remote_events)
            
            # Update sync timestamp
            self.last_sync = datetime.utcnow()
            self._log_sync('pull', merged_count)
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = {
                'success': True,
                'events_merged': merged_count,
                'duration_ms': duration,
                'last_sync': self.last_sync.isoformat()
            }
            
            logger.info(f"Pull sync completed: {merged_count} events in {duration:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Pull sync failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'events_merged': 0
            }
    
    def push_sync(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Push local events to be synced to remote.
        
        Args:
            since: Get events since this timestamp (uses last_sync if None)
            
        Returns:
            Dictionary with events to push
        """
        try:
            sync_since = since or self.last_sync or (datetime.utcnow() - timedelta(days=30))
            
            # Get local changes since last sync
            local_events = self.crdt_manager.get_changes_since(sync_since)
            
            result = {
                'success': True,
                'events_count': len(local_events),
                'events': [event.to_dict() for event in local_events],
                'node_id': self.node_id,
                'since': sync_since.isoformat()
            }
            
            logger.info(f"Push sync prepared: {len(local_events)} events")
            return result
            
        except Exception as e:
            logger.error(f"Push sync failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'events_count': 0
            }
    
    def bidirectional_sync(self, remote_events: List[Event],
                          since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Perform bidirectional sync: pull remote and return local events.
        
        Args:
            remote_events: Events from remote node
            since: Timestamp for local changes
            
        Returns:
            Sync result with local events to push
        """
        try:
            start_time = datetime.utcnow()
            
            # Pull remote events
            pull_result = self.pull_sync(remote_events)
            
            # Prepare local events for push
            push_result = self.push_sync(since)
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = {
                'success': True,
                'pull': {
                    'events_merged': pull_result.get('events_merged', 0)
                },
                'push': {
                    'events_count': push_result.get('events_count', 0),
                    'events': push_result.get('events', [])
                },
                'duration_ms': duration,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None
            }
            
            logger.info(f"Bidirectional sync completed in {duration:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Bidirectional sync failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def auto_sync(self, remote_endpoint: Optional[str] = None,
                  interval_seconds: int = 60) -> Dict[str, Any]:
        """
        Prepare for automatic periodic synchronization.
        
        Args:
            remote_endpoint: URL or identifier of remote sync endpoint
            interval_seconds: Sync interval in seconds
            
        Returns:
            Auto-sync configuration
        """
        config = {
            'enabled': True,
            'interval_seconds': interval_seconds,
            'remote_endpoint': remote_endpoint,
            'node_id': self.node_id,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
        
        logger.info(f"Auto-sync configured: {config}")
        return config
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            Status information
        """
        try:
            # Get last sync record from database
            query = """
            SELECT last_sync, events_synced, sync_direction
            FROM crdt_sync_log
            WHERE node_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            
            rows = self.db.execute_query(query, (self.node_id,))
            
            if rows:
                last_record = rows[0]
                status = {
                    'node_id': self.node_id,
                    'last_sync': last_record['last_sync'].isoformat() if last_record['last_sync'] else None,
                    'events_synced': last_record['events_synced'],
                    'direction': last_record['sync_direction'],
                    'is_synced': True
                }
            else:
                status = {
                    'node_id': self.node_id,
                    'last_sync': None,
                    'events_synced': 0,
                    'direction': 'none',
                    'is_synced': False
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}", exc_info=True)
            return {
                'node_id': self.node_id,
                'error': str(e),
                'is_synced': False
            }
    
    def _log_sync(self, direction: str, events_synced: int) -> None:
        """
        Log sync operation to database.
        
        Args:
            direction: 'pull', 'push', or 'bidirectional'
            events_synced: Number of events synchronized
        """
        try:
            query = """
            INSERT INTO crdt_sync_log (node_id, last_sync, events_synced, sync_direction)
            VALUES (%s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (
                self.node_id,
                datetime.utcnow(),
                events_synced,
                direction
            ))
            
        except Exception as e:
            logger.error(f"Failed to log sync: {e}")
    
    def resolve_conflicts(self, entity_id: str) -> bool:
        """
        Manually trigger conflict resolution for an entity.
        
        Args:
            entity_id: Entity to resolve conflicts for
            
        Returns:
            True if successful
        """
        try:
            # Rebuild state from events (this will merge all events)
            register = self.crdt_manager.rebuild_state_from_events(entity_id)
            
            if register:
                # Save resolved state
                self.crdt_manager.registers[entity_id] = register
                self.crdt_manager._save_current_state(entity_id, register)
                logger.info(f"Resolved conflicts for entity {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve conflicts: {e}", exc_info=True)
            return False
    
    def get_pending_changes(self) -> List[str]:
        """
        Get list of entities with pending changes since last sync.
        
        Returns:
            List of entity IDs with changes
        """
        try:
            sync_since = self.last_sync or (datetime.utcnow() - timedelta(days=30))
            
            query = """
            SELECT DISTINCT entity_id
            FROM crdt_events
            WHERE timestamp > %s AND node_id = %s
            ORDER BY entity_id
            """
            
            rows = self.db.execute_query(query, (sync_since, self.node_id))
            
            entity_ids = [row['entity_id'] for row in rows]
            logger.debug(f"Found {len(entity_ids)} entities with pending changes")
            
            return entity_ids
            
        except Exception as e:
            logger.error(f"Failed to get pending changes: {e}", exc_info=True)
            return []
