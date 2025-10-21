"""
CRDT Types Package - Various Conflict-Free Replicated Data Type implementations
"""

from .g_counter import GCounter
from .pn_counter import PNCounter
from .g_set import GSet
from .two_phase_set import TwoPhaseSet
from .or_set import ORSet
from .lww import LWWElementSet

# Export all CRDT classes
__all__ = [
    'GCounter',
    'PNCounter', 
    'GSet',
    'TwoPhaseSet',
    'ORSet',
    'LWWElementSet'
]

# CRDT type registry
CRDT_REGISTRY = {
    'g_counter': GCounter,
    'pn_counter': PNCounter,
    'g_set': GSet,
    'two_phase_set': TwoPhaseSet,
    'or_set': ORSet,
    'lww': lww
}

def get_crdt_class(crdt_type):
    """
    Get CRDT class by type name
    
    Args:
        crdt_type (str): Type of CRDT ('g_counter', 'pn_counter', etc.)
    
    Returns:
        class: CRDT class or None if not found
    """
    return CRDT_REGISTRY.get(crdt_type)

def get_available_types():
    """
    Get list of available CRDT types
    
    Returns:
        list: Available CRDT type names
    """
    return list(CRDT_REGISTRY.keys())

def create_crdt_instance(crdt_type, node_id, sync_folder):
    """
    Factory function to create CRDT instance
    
    Args:
        crdt_type (str): Type of CRDT
        node_id (str): Node identifier
        sync_folder (str): Synchronization folder path
    
    Returns:
        BaseCRDT: CRDT instance
    """
    crdt_class = get_crdt_class(crdt_type)
    if not crdt_class:
        raise ValueError(f"Unknown CRDT type: {crdt_type}")
    
    return crdt_class(node_id, sync_folder)

# Package description
__description__ = "Various CRDT implementations for different synchronization needs"
__version__ = "1.0.0"
