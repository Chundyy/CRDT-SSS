#!/usr/bin/env python3
"""
PROPER Minimal 2P-Set (Two-Phase Set) CRDT Implementation
"""

from ..base_crdt import BaseCRDT


class TwoPhaseSet(BaseCRDT):
    """
    Proper Two-Phase Set CRDT - True to the mathematical definition
    """

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.added = set()  # All elements ever added (grow-only)
        self.removed = set()  # All elements ever removed (grow-only)

    def add(self, element):
        """Add element to added set - ALWAYS allowed"""
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

    def get_active_elements(self):
        """Get all active elements"""
        return self.added - self.removed

    def merge(self, other_state):
        """Merge with another 2P-Set state - simple set union"""
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
        active = self.added - self.removed
        return f"2P-Set: {len(active)} active, {len(self.removed)} removed"

    def update_local_state(self):
        """
        Required by BaseCRDT - but does NOT sync with filesystem
        That would violate 2P-Set semantics
        """
        self.logger.debug("update_local_state - No filesystem sync in proper 2P-Set")
        # Empty - 2P-Set should not auto-detect files