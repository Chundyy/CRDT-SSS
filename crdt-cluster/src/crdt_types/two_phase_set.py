#!/usr/bin/env python3
"""
Minimal 2P-Set (Two-Phase Set) CRDT Implementation
"""

from ..base_crdt import BaseCRDT

class TwoPhaseSet(BaseCRDT):
    """
    Minimal Two-Phase Set CRDT - Only core 2P-Set functionality
    """
    
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.added = set()    # All elements ever added
        self.removed = set()  # All elements ever removed

    def add(self, element):
        """Add element to added set (always allowed in 2P-Set)"""
        self.added.add(element)
        self.logger.info(f"Added: {element}")
        return True

    def remove(self, element):
        """Remove element - only if it exists in added set"""
        if element in self.added:
            self.removed.add(element)
            self.logger.info(f"Removed: {element}")
            return True
        self.logger.warning(f"Cannot remove {element} - not in added set")
        return False

    def lookup(self, element):
        """Check if element is in active set"""
        return element in self.added and element not in self.removed

    def get_elements(self):
        """Get all active elements"""
        return self.added - self.removed

    def merge(self, other_state):
        """Merge with another 2P-Set state"""
        # Both sets are grow-only - simple union operations
        self.added |= set(other_state.get('added', []))
        self.removed |= set(other_state.get('removed', []))
        
        self.logger.info(f"Merged: {len(self.added)} added, {len(self.removed)} removed")

    def to_dict(self):
        """Convert state to dictionary"""
        return {
            'added': list(self.added),
            'removed': list(self.removed)
        }

    def from_dict(self, state):
        """Load state from dictionary"""
        self.added = set(state.get('added', []))
        self.removed = set(state.get('removed', []))

    def get_state_summary(self):
        """Get state summary"""
        active = len(self.added - self.removed)
        return f"2P-Set: {active} active, {len(self.removed)} removed"

    def update_local_state(self):
        """
        Required by BaseCRDT - minimal implementation
        """
        self.logger.info("update_local_state called - no file sync in minimal version")
        # Empty implementation since we're keeping it minimal
        # You can add basic file sync here if needed