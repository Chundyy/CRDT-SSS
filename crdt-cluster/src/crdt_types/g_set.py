#!/usr/bin/env python3
"""
G-Set (Grow-only Set) CRDT implementation
"""
from pathlib import Path
from ..base_crdt import BaseCRDT

class GSet(BaseCRDT):
    """Grow-only Set CRDT - elements can be added but never removed"""
    
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.elements = set()
        
    def add(self, element):
        """Add an element to the set"""
        if element not in self.elements:
            self.elements.add(element)
            self.logger.info(f"Added element: {element}")
            return True
        return False
    
    def query(self):
        """Get all elements in the set"""
        return self.elements.copy()
    
    def contains(self, element):
        """Check if element is in set"""
        return element in self.elements
    
    def update_local_state(self):
        """Scan sync folder for files and add them to the set"""
        try:
            for file_path in self.sync_folder.rglob('*'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.sync_folder))
                    if relative_path not in self.elements:
                        self.elements.add(relative_path)
                        self.logger.debug(f"Added file to G-Set: {relative_path}")
        except Exception as e:
            self.logger.error(f"Error scanning folder: {e}")
    
    def merge(self, other_state):
        """Merge another GSet state"""
        other_elements = set(other_state.get('elements', []))
        if other_elements - self.elements:
            self.elements |= other_elements
            self.logger.info(f"Merged G-Set state, now has {len(self.elements)} elements")
            return True
        return False
    
    def to_dict(self):
        return {'elements': list(self.elements)}
    
    def from_dict(self, data):
        self.elements.clear()
        self.elements.update(data.get('elements', []))
        self.logger.info(f"Loaded G-Set state with {len(self.elements)} elements")
    
    def get_state_summary(self):
        return f"G-Set Elements: {len(self.elements)} items"
