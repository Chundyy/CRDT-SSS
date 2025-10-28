#!/usr/bin/env python3
"""
Base CRDT class with common functionality
"""
import json
import time
import threading
import logging
import socket
import pickle
import os
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

class BaseCRDT(ABC):
    """Abstract base class for all CRDT types"""
    
    def __init__(self, node_id, sync_folder):
        self.node_id = node_id
        self.sync_folder = Path(sync_folder)
        self.sync_folder.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{node_id}")
        
    @abstractmethod
    def update_local_state(self):
        """Update CRDT state with current folder contents"""
        pass
    
    @abstractmethod
    def merge(self, other_state):
        """Merge another node's state"""
        pass
    
    @abstractmethod
    def to_dict(self):
        """Convert state to dictionary for serialization"""
        pass
    
    @abstractmethod
    def from_dict(self, data):
        """Load state from dictionary"""
        pass
    
    @abstractmethod
    def get_state_summary(self):
        """Get human-readable state summary"""
        pass

class BaseCRDTNode:
    """Base node implementation for all CRDT types"""
    
    def __init__(self, config_file, crdt_class):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Setup logging
        try:
            import logging.config
            logging_config = self.config.get('logging_config', '')
            if os.path.exists(logging_config):
                logging.config.fileConfig(logging_config)
            else:
                raise FileNotFoundError(f"Logging config not found: {logging_config}")
        except Exception as e:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
            logging.getLogger().info(f"Using basic console logging: {e}")
        
        self.logger = logging.getLogger(f"CRDTNode.{self.config['node_id']}")
        
        # Initialize CRDT
        self.node_id = self.config['node_id']
        self.sync_folder = self.config['sync_folder']
        self.crdt = crdt_class(self.node_id, self.sync_folder)
        
        # Networking
        self.host = self.config['host']
        self.port = self.config['port']
        self.peers = self.config['peers']
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        
        self.running = True
        self.sync_interval = self.config.get('sync_interval', 10)
        self.scan_interval = self.config.get('scan_interval', 30)
        
        # State management
        self.state_file = self.config['state_file']
        self._load_state()
        
        self.logger.info(f"{crdt_class.__name__} node {self.node_id} initialized")
        self.logger.info(f"Sync folder: {self.sync_folder}")
        self.logger.info(f"Host: {self.host}:{self.port}")
        
    def _load_state(self):
        """Load state from disk"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
                self.crdt.from_dict(state_data)
                self.logger.info(f"State loaded from {self.state_file}")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.crdt.to_dict(), f, indent=2)
            self.logger.debug("State saved to disk")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def start(self):
        """Start the CRDT node"""
        try:
            self.socket.bind((self.host, self.port))
            self.logger.info(f"Socket bound to {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to bind socket to {self.host}:{self.port}: {e}")
            raise
        
        # Start threads
        threads = [
            threading.Thread(target=self._listen, name="Listener", daemon=True),
            threading.Thread(target=self._periodic_sync, name="Sync", daemon=True),
            threading.Thread(target=self._periodic_scan, name="Scanner", daemon=True),
            threading.Thread(target=self._periodic_save, name="Save", daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        self.logger.info(f"CRDT node {self.node_id} started")
        
    def _listen(self):
        """Listen for incoming messages"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65507)
                message = pickle.loads(data)
                self._handle_message(message, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error receiving message: {e}")
    
    def _handle_message(self, message, addr):
        """Handle incoming messages"""
        msg_type = message.get('type')
        
        if msg_type == 'state_sync':
            self.logger.info(f"Received state sync from {addr[0]}:{addr[1]}")
            if self.crdt.merge(message['state']):
                self.logger.info(f"State synchronized from {addr[0]}:{addr[1]}")
            
            # Send acknowledgment
            ack_msg = {
                'type': 'ack',
                'node_id': self.node_id,
                'timestamp': datetime.now().isoformat()
            }
            try:
                self.socket.sendto(pickle.dumps(ack_msg), addr)
            except Exception as e:
                self.logger.error(f"Failed to send ACK: {e}")
            
        elif msg_type == 'ack':
            self.logger.debug(f"Received ACK from {message['node_id']}")
            
        else:
            self.logger.warning(f"Unknown message type: {msg_type}")
    
    def _periodic_sync(self):
        """Periodically sync with peers"""
        while self.running:
            time.sleep(self.sync_interval)
            self.sync_with_peers()
    
    def _periodic_scan(self):
        """Periodically scan for changes"""
        while self.running:
            time.sleep(self.scan_interval)
            self.crdt.update_local_state()
            self.logger.debug("State scan completed")
    
    def _periodic_save(self):
        """Periodically save state to disk"""
        while self.running:
            time.sleep(30)
            self._save_state()
    
    def sync_with_peers(self):
        """Sync state with all peers"""
        self.crdt.update_local_state()
        
        state_data = {
            'type': 'state_sync',
            'node_id': self.node_id,
            'state': self.crdt.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        message = pickle.dumps(state_data)
        success_count = 0
        
        for peer in self.peers:
            try:
                self.socket.sendto(message, (peer['host'], peer['port']))
                success_count += 1
                self.logger.debug(f"Sent sync to {peer['host']}:{peer['port']}")
            except Exception as e:
                self.logger.error(f"Failed to sync with {peer['host']}:{peer['port']}: {e}")
        
        if success_count > 0:
            self.logger.info(f"State synced with {success_count}/{len(self.peers)} peers")
    
    def stop(self):
        """Stop the node"""
        self.running = False
        self._save_state()
        self.socket.close()
        self.logger.info("CRDT node stopped")
    
    def get_state_summary(self):
        """Get human-readable state summary"""
        return self.crdt.get_state_summary()
