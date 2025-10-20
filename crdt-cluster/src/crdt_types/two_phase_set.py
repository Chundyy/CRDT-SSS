"""
Simplified Two-Phase Set (2P-Set) CRDT implementation.
"""

from ..base_crdt import BaseCRDT

class TwoPhaseSet(BaseCRDT):
    def __init__(self, node_id, sync_folder):
        """Initialize the Two-Phase Set with empty added and removed sets."""
        super().__init__(node_id, sync_folder)
        self.added = set()
        self.removed = set()

    def add(self, element):
        """Add an element to the set if it is not already removed."""
        if element not in self.removed:
            self.added.add(element)
            self.logger.info(f"Added element: {element}")
            return True
        self.logger.warning(f"Cannot add {element} - it's in removed set")
        return False

    def remove(self, element):
        """Remove an element from the set if it exists in the added set."""
        if element in self.added:
            self.removed.add(element)
            self.logger.info(f"Removed element: {element}")
            return True
        self.logger.warning(f"Cannot remove {element} - not in added set")
        return False

    def merge(self, other_state):
        """Merge another Two-Phase Set state into this one."""
        remote_added = set(other_state.get('added', []))
        remote_removed = set(other_state.get('removed', []))

        # Merge added elements
        new_additions = remote_added - self.removed
        self.added |= new_additions
        self.logger.info(f"Merged new additions: {new_additions}")

        # Merge removed elements
        new_removals = remote_removed - self.removed
        self.removed |= new_removals
        self.added -= new_removals  # Ensure consistency by removing elements marked as removed
        self.logger.info(f"Merged new removals: {new_removals}")

        self.logger.info("Merged state with remote")

    def to_dict(self):
        """Convert the Two-Phase Set state to a dictionary."""
        return {
            'added': list(self.added),
            'removed': list(self.removed)
        }

    def from_dict(self, state):
        """Load the Two-Phase Set state from a dictionary."""
        self.added = set(state.get('added', []))
        self.removed = set(state.get('removed', []))
        self.logger.info("Loaded state from dictionary")

    def update_local_state(self):
        """Update CRDT state with current folder contents."""
        try:
            current_files = {file.name for file in self.sync_folder.iterdir() if file.is_file()}
            self.logger.info(f"Current files in sync folder: {current_files}")

            # Identify new files to add
            new_files = current_files - self.added
            for file in new_files:
                if file not in self.removed:  # Only add if not explicitly removed
                    self.add(file)

            # Identify files to remove
            missing_files = self.added - current_files
            for file in missing_files:
                if file not in self.removed:  # Avoid marking as removed if already removed
                    self.logger.info(f"File missing but not marking as removed: {file}")

            self.logger.info("Local state updated based on folder contents")
        except Exception as e:
            self.logger.error(f"Error updating local state: {e}")

    def get_state_summary(self):
        """Get human-readable state summary."""
        active = self.added - self.removed
        return f"2P-Set: {len(active)} active, {len(self.removed)} removed, {len(self.added)} total added"
