"""
Simplified Two-Phase Set (2P-Set) CRDT implementation.
"""

class TwoPhaseSet:
    def __init__(self):
        """Initialize the Two-Phase Set with empty added and removed sets."""
        self.added = set()
        self.removed = set()

    def add(self, element):
        """Add an element to the set if it is not already removed."""
        if element not in self.removed:
            self.added.add(element)
            return True
        return False

    def remove(self, element):
        """Remove an element from the set if it exists in the added set."""
        if element in self.added:
            self.removed.add(element)
            return True
        return False

    def merge(self, other_state):
        """Merge another Two-Phase Set state into this one."""
        self.added |= set(other_state.get('added', []))
        self.removed |= set(other_state.get('removed', []))
        self.added -= self.removed  # Ensure consistency by removing elements marked as removed

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

    def sync_file_content(self, file_content):
        """Synchronize the Two-Phase Set with the content of a file."""
        current_elements = set(file_content.splitlines())
        new_elements = current_elements - self.added
        removed_elements = self.added - current_elements

        for element in new_elements:
            self.add(element)

        for element in removed_elements:
            self.remove(element)

    def get_active_elements(self):
        """Get the active elements in the set (added but not removed)."""
        return self.added - self.removed
