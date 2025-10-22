"""
CRDT-enabled File Handler for NetGuardian

Extends FileHandler with CRDT capabilities for distributed file management.
Wraps file operations with event sourcing and conflict-free replication.
"""

import os
from typing import Tuple, Dict, Any, Optional, List
import logging
from datetime import datetime

from src.file_manager.file_handler import FileHandler
from src.crdt import CRDTManager, SyncEngine

logger = logging.getLogger(__name__)


class CRDTFileHandler(FileHandler):
    """
    CRDT-enabled file handler with automatic conflict resolution.
    
    Extends FileHandler to provide:
    - Distributed state management with CRDTs
    - Automatic conflict resolution
    - Event sourcing for audit trail
    - Multi-device synchronization support
    
    All file operations are tracked as CRDT events for eventual consistency.
    """
    
    def __init__(self, db_manager, user_id: int, node_id: Optional[str] = None):
        """
        Initialize CRDT File Handler.
        
        Args:
            db_manager: Database manager instance
            user_id: User ID for file operations
            node_id: Optional node identifier for this device
        """
        # Initialize parent FileHandler
        super().__init__(db_manager, user_id)
        
        # Initialize CRDT components
        self.crdt_manager = CRDTManager(db_manager, node_id)
        self.sync_engine = SyncEngine(self.crdt_manager)
        
        logger.info(f"CRDTFileHandler initialized for user {user_id}, node {self.crdt_manager.node_id}")
    
    def upload_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Upload file with CRDT state tracking.
        
        Args:
            file_path: Path to file to upload
            
        Returns:
            (success, message) tuple
        """
        # Call parent upload
        success, message = super().upload_file(file_path)
        
        if success:
            try:
                # Extract file info from message or database
                file_info = self._get_latest_file_info()
                
                if file_info:
                    # Create CRDT state for this file
                    file_id = f"file_{file_info['id']}"
                    metadata = {
                        'file_id': file_info['id'],
                        'filename': file_info['filename'],
                        'original_name': file_info['original_name'],
                        'file_size': file_info['file_size'],
                        'file_hash': file_info.get('file_hash'),
                        'upload_date': file_info['upload_date'].isoformat() if isinstance(file_info['upload_date'], datetime) else file_info['upload_date'],
                        'user_id': self.user_id,
                        'deleted': False
                    }
                    
                    self.crdt_manager.create_file_state(file_id, metadata)
                    logger.info(f"Created CRDT state for file {file_id}")
                    
            except Exception as e:
                logger.error(f"Failed to create CRDT state after upload: {e}", exc_info=True)
                # Don't fail the upload if CRDT tracking fails
        
        return success, message
    
    def delete_file(self, file_id: int) -> Tuple[bool, str]:
        """
        Delete file with CRDT tombstone.
        
        Args:
            file_id: Database file ID
            
        Returns:
            (success, message) tuple
        """
        # Call parent delete
        success, message = super().delete_file(file_id)
        
        if success:
            try:
                # Mark as deleted in CRDT
                crdt_file_id = f"file_{file_id}"
                self.crdt_manager.delete_file_state(crdt_file_id)
                logger.info(f"Marked file {crdt_file_id} as deleted in CRDT")
                
            except Exception as e:
                logger.error(f"Failed to mark file as deleted in CRDT: {e}", exc_info=True)
        
        return success, message
    
    def sync_with_remote(self, remote_events: List[Dict]) -> Dict[str, Any]:
        """
        Synchronize file states with remote node.
        
        Args:
            remote_events: List of event dictionaries from remote
            
        Returns:
            Sync result dictionary
        """
        try:
            from src.crdt.event_store import Event
            
            # Convert dicts to Event objects
            events = [Event.from_dict(e) for e in remote_events]
            
            # Perform bidirectional sync
            result = self.sync_engine.bidirectional_sync(events)
            
            logger.info(f"Sync completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            Status dictionary
        """
        return self.sync_engine.get_sync_status()
    
    def get_file_state(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        Get CRDT state for a file.
        
        Args:
            file_id: Database file ID
            
        Returns:
            File state dictionary or None
        """
        crdt_file_id = f"file_{file_id}"
        return self.crdt_manager.get_file_state(crdt_file_id)
    
    def resolve_conflicts(self, file_id: int) -> bool:
        """
        Manually resolve conflicts for a file.
        
        Args:
            file_id: Database file ID
            
        Returns:
            True if successful
        """
        crdt_file_id = f"file_{file_id}"
        return self.sync_engine.resolve_conflicts(crdt_file_id)
    
    def get_pending_sync_changes(self) -> List[str]:
        """
        Get list of files with pending sync changes.
        
        Returns:
            List of file IDs with pending changes
        """
        return self.sync_engine.get_pending_changes()
    
    def enable_auto_sync(self, remote_endpoint: str, interval_seconds: int = 60) -> Dict[str, Any]:
        """
        Enable automatic synchronization.
        
        Args:
            remote_endpoint: Remote sync endpoint URL
            interval_seconds: Sync interval in seconds
            
        Returns:
            Auto-sync configuration
        """
        return self.sync_engine.auto_sync(remote_endpoint, interval_seconds)
    
    def get_crdt_statistics(self) -> Dict[str, Any]:
        """
        Get CRDT system statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self.crdt_manager.get_statistics()
        sync_status = self.sync_engine.get_sync_status()
        
        return {
            'crdt': stats,
            'sync': sync_status,
            'user_id': self.user_id
        }
    
    def _get_latest_file_info(self) -> Optional[Dict[str, Any]]:
        """
        Get info for the most recently uploaded file.
        
        Returns:
            File info dictionary or None
        """
        try:
            query = """
            SELECT id, filename, original_name, file_size, file_hash, upload_date
            FROM files
            WHERE user_id = %s
            ORDER BY upload_date DESC
            LIMIT 1
            """
            
            rows = self.db_manager.execute_query(query, (self.user_id,))
            
            if rows:
                return dict(rows[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest file info: {e}")
            return None
