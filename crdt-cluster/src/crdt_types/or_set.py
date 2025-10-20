#!/usr/bin/env python3
"""
OR-Set (Observed-Removed Set) CRDT implementation
"""
import uuid
import time
from collections import defaultdict
from pathlib import Path
from ..base_crdt import BaseCRDT

class ORSet(BaseCRDT):
    """Observed-Removed Set CRDT - better handling of add/remove operations"""
    
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.elements = {}  # element -> set of unique tags
        self.removed_tags = set()  # tags that have been removed
        
    def add(self, element):
        """Add an element to the set"""
        tag = f"{self.node_id}_{time.time()}_{uuid.uuid4().hex[:8]}"
        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add(tag)
        self.logger.info(f"Added element: {element} with tag {tag}")
        return True
    
    def remove(self, element):
        """Remove an element from the set"""
        if element in self.elements:
            # Move all tags to removed set
            tags_to_remove = self.elements[element]
            self.removed_tags.update(tags_to_remove)
            del self.elements[element]
            self.logger.info(f"Removed element: {element}")
            return True
        return False
    
    def query(self):
        """Get all active elements in the set"""
        return set(self.elements.keys())
    
    def update_local_state(self):
        """Scan sync folder and manage OR-Set based on file presence"""
        try:
            current_files = set()
            for file_path in self.sync_folder.rglob('*'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.sync_folder))
                    current_files.add(relative_path)
            
            # Add new files
            for filename in current_files - set(self.elements.keys()):
                self.add(filename)
            
            # Remove missing files
            for filename in set(self.elements.keys()) - current_files:
                self.remove(filename)
                
        except Exception as e:
            self.logger.error(f"Error scanning folder: {e}")
    
    def merge(self, other_state):
        """Merge another ORSet state"""
        merged = False
        
        # Merge elements
        for element, tags in other_state.get('elements', {}).items():
            if element not in self.elements:
                self.elements[element] = set()
            original_size = len(self.elements[element])
            self.elements[element].update(tags)
            if len(self.elements[element]) > original_size:
                merged = True
        
        # Merge removed tags
        other_removed = set(other_state.get('removed_tags', []))
        original_removed_size = len(self.removed_tags)
        self.removed_tags.update(other_removed)
        if len(self.removed_tags) > original_removed_size:
            merged = True
        
        # Clean up elements that have all tags removed
        elements_to_remove = []
        for element, tags in self.elements.items():
            if all(tag in self.removed_tags for tag in tags):
                elements_to_remove.append(element)
        
        for element in elements_to_remove:
            del self.elements[element]
            merged = True
        
        if merged:
            active_count = len(self.elements)
            self.logger.info(f"Merged OR-Set state, now has {active_count} active elements")
        
        return merged
    
    def to_dict(self):
        return {
            'elements': {element: list(tags) for element, tags in self.elements.items()},
            'removed_tags': list(self.removed_tags)
        }
    
    def from_dict(self, data):
        self.elements.clear()
        self.removed_tags.clear()
        
        for element, tags in data.get('elements', {}).items():
            self.elements[element] = set(tags)
        
        self.removed_tags.update(data.get('removed_tags', []))
        self.logger.info(f"Loaded OR-Set state with {len(self.elements)} active elements")
    
    def get_state_summary(self):
        return f"OR-Set: {len(self.elements)} active elements, {len(self.removed_tags)} removed tags"
