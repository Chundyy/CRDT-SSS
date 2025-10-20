"""
Two-Phase Set (2P-Set) CRDT implementation for distributed systems.
"""

from ..base_crdt import BaseCRDT


class TwoPhaseSet(BaseCRDT):
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.added = set()
        self.removed = set()

    def add(self, element):
        """Add an element to the added set (ALWAYS allowed in 2P-Set)."""
        self.added.add(element)  # No condition check!
        self.logger.info(f"Added element: {element}")
        return True

    def remove(self, element):
        """Remove an element - only allowed if it's in the added set."""
        if element in self.added:
            self.removed.add(element)
            self.logger.info(f"Removed element: {element}")
            return True
        self.logger.warning(f"Cannot remove {element} - not in added set")
        return False

    def merge(self, other_state):
        """Merge another 2P-Set state - both sets are grow-only."""
        remote_added = set(other_state.get('added', []))
        remote_removed = set(other_state.get('removed', []))

        # Simply union both sets (both are monotonic)
        self.added |= remote_added
        self.removed |= remote_removed

        self.logger.info(f"Merged: +{len(remote_added)} added, +{len(remote_removed)} removed")

    def lookup(self, element):
        """Check if element is in the active set."""
        return element in self.added and element not in self.removed

    def get_active_elements(self):
        """Get all currently active elements."""
        return self.added - self.removed

    def to_dict(self):
        return {
            'added': list(self.added),
            'removed': list(self.removed)
        }

    def from_dict(self, state):
        self.added = set(state.get('added', []))
        self.removed = set(state.get('removed', []))