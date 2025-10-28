#!/usr/bin/env python3
"""
CRDT Service Wrapper - supports multiple CRDT types
"""
import sys
import os
import time
import signal
import logging
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import CRDT types - CHANGED: types -> crdt_types
    from src.crdt_types.g_counter import GCounter
    from src.crdt_types.g_set import GSet
    from src.crdt_types.two_phase_set import TwoPhaseSet
    from src.base_crdt import BaseCRDTNode
    from src.crdt_types.lww import LWWFileSync

except ImportError as e:
    print(f"CRITICAL: Import error: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

# CRDT type mapping
CRDT_TYPES = {
    'g_counter': GCounter,
    'g_set': GSet,
    'two_phase_set': TwoPhaseSet,
    'lww': LWWFileSync
}

class CRDTService:
    def __init__(self, config_path):
        self.config_path = config_path
        self.node = None
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.node:
            self.node.stop()
            
    def run(self):
        """Main service loop"""
        try:
            logging.info(f"Starting CRDT service with config: {self.config_path}")
            
            # Verify config file exists
            if not os.path.exists(self.config_path):
                logging.error(f"Config file not found: {self.config_path}")
                return 1
            
            # Load configuration and determine CRDT type
            import json
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            crdt_type_name = config.get('crdt_type', 'g_counter')
            crdt_class = CRDT_TYPES.get(crdt_type_name)
            
            if not crdt_class:
                logging.error(f"Unknown CRDT type: {crdt_type_name}")
                logging.error(f"Available types: {', '.join(CRDT_TYPES.keys())}")
                return 1
            
            logging.info(f"Using CRDT type: {crdt_type_name}")
            
            # Initialize and start node
            self.node = BaseCRDTNode(self.config_path, crdt_class)
            self.node.start()
            
            logging.info(f"CRDT service started successfully with {crdt_type_name}")
            
            # Main service loop
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            logging.error(f"CRDT service error: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return 1
        finally:
            if self.node:
                self.node.stop()
            logging.info("CRDT service stopped")
            
        return 0

def setup_logging():
    """Setup basic logging for service"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def main():
    if len(sys.argv) != 2:
        print("Usage: crdt_service.py <config_file>")
        print("Available CRDT types: g_counter, pn_counter, g_set, two_phase_set, or_set")
        sys.exit(1)
        
    # Setup logging first
    setup_logging()
    
    config_file = sys.argv[1]
    service = CRDTService(config_file)
    sys.exit(service.run())

if __name__ == "__main__":
    main()
