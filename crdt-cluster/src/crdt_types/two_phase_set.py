#!/usr/bin/env python3
"""
2P-Set (Two-Phase Set) CRDT implementation
"""
from pathlib import Path
from ..base_crdt import BaseCRDT


class TwoPhaseSet(BaseCRDT):
    """Two-Phase Set CRDT - supports add and remove operations"""

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.added = set()
        self.removed = set()

    def add(self, element):
        """Add an element to the set"""
        if element not in self.removed:
            self.added.add(element)
            self.logger.info(f"Added element: {element}")
            return True
        self.logger.warning(f"Cannot add {element} - it's in removed set")
        return False

    def remove(self, element):
        """Remove an element from the set"""
        if element in self.added and element not in self.removed:
            self.removed.add(element)
            self.logger.info(f"Removed element: {element}")
            return True
        self.logger.warning(f"Cannot remove {element} - not in added set or already removed")
        return False

    def update_local_state(self):
        """Scan sync folder and manage set based on file presence"""
        try:
            self.logger.info("=== Starting folder scan ===")

            current_files = set()
            scan_path = Path(self.sync_folder)

            self.logger.info(f"Scanning folder: {scan_path.absolute()}")
            self.logger.info(f"Folder exists: {scan_path.exists()}")
            self.logger.info(f"Folder is directory: {scan_path.is_dir()}")

            # List all files found
            for file_path in scan_path.rglob('*'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(scan_path))
                    current_files.add(relative_path)
                    self.logger.info(f"FOUND FILE: {relative_path} (size: {file_path.stat().st_size})")

            self.logger.info(f"Scan complete: {len(current_files)} files found")
            self.logger.info(f"Files found: {list(current_files)}")

            # Debug current state
            self.logger.info(f"Current state - Added: {len(self.added)}, Removed: {len(self.removed)}")
            self.logger.info(f"Added set: {list(self.added)}")
            self.logger.info(f"Removed set: {list(self.removed)}")

            # Add new files that aren't in removed set
            new_files = current_files - self.added
            self.logger.info(f"New files to add: {list(new_files)}")

            for filename in new_files:
                if filename not in self.removed:
                    self.added.add(filename)
                    self.logger.info(f"✅ AUTO-ADDED: {filename}")
                else:
                    self.logger.warning(f"❌ Cannot add {filename} - in removed set")

            # Remove files that are missing but only if they were previously added
            missing_files = self.added - current_files
            self.logger.info(f"Missing files to remove: {list(missing_files)}")

            for filename in missing_files:
                if filename not in self.removed:
                    self.removed.add(filename)
                    self.logger.info(f"🔄 AUTO-REMOVED: {filename}")
                else:
                    self.logger.warning(f"⚠️  Already removed: {filename}")

            # Final state
            active_files = self.added - self.removed
            self.logger.info(f"=== Scan complete ===")
            self.logger.info(f"Active files: {len(active_files)}")
            self.logger.info(f"Final - Added: {len(self.added)}, Removed: {len(self.removed)}")

        except Exception as e:
            self.logger.error(f"❌ Error scanning folder: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def merge(self, other_state):
        """Merge another TwoPhaseSet state"""
        merged = False

        other_added = set(other_state.get('added', []))
        other_removed = set(other_state.get('removed', []))

        self.logger.info(f"=== Merging state ===")
        self.logger.info(f"Remote added: {len(other_added)}")
        self.logger.info(f"Remote removed: {len(other_removed)}")

        # Ensure elements in 'removed' are not re-added
        valid_additions = other_added - self.removed
        if valid_additions:
            self.added |= valid_additions
            self.logger.info(f"\U0001f4e5 Merged new additions: {list(valid_additions)}")
            merged = True

        # Merge 'removed' set, but exclude files that exist in both 'added' sets
        valid_removals = other_removed - self.added
        if valid_removals:
            self.removed |= valid_removals
            self.logger.info(f"\U0001f5d1 Merged new removals: {list(valid_removals)}")
            merged = True

        return merged

    def to_dict(self):
        return {
            'added': list(self.added),
            'removed': list(self.removed)
        }

    def from_dict(self, data):
        self.added.clear()
        self.removed.clear()
        self.added.update(data.get('added', []))
        self.removed.update(data.get('removed', []))
        active_count = len(self.added - self.removed)
        self.logger.info(f"📂 Loaded 2P-Set: {active_count} active, {len(self.removed)} removed")

    def get_state_summary(self):
        active = self.added - self.removed
        return f"2P-Set: {len(active)} active, {len(self.removed)} removed, {len(self.added)} total added"

