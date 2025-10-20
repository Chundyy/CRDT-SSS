"""
CRDT Cluster - A distributed state-based CRDT implementation for file synchronization
"""

__version__ = "1.0.0"
__author__ = "CRDT Cluster Team"
__description__ = "State-based CRDT implementation for distributed file synchronization"

# Import main classes for easier access
from .base_crdt import BaseCRDT, BaseCRDTNode

# Package-level imports
import logging

# Set up package-level logger
logger = logging.getLogger(__name__)

def get_crdt_types():
    """
    Return available CRDT types
    """
    return {
        'g_counter': 'Grow-only Counter',
        'pn_counter': 'Positive-Negative Counter', 
        'g_set': 'Grow-only Set',
        'two_phase_set': 'Two-Phase Set',
        'or_set': 'Observed-Removed Set'
    }

def create_node(config_file, crdt_type):
    """
    Factory function to create a CRDT node of specified type
    """
    from .crdt_types import get_crdt_class  # CHANGED: types -> crdt_types
    
    crdt_class = get_crdt_class(crdt_type)
    if not crdt_class:
        raise ValueError(f"Unknown CRDT type: {crdt_type}")
    
    return BaseCRDTNode(config_file, crdt_class)

# Package initialization
logger.info("CRDT Cluster package initialized")
