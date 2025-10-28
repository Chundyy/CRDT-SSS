#!/usr/bin/env python3
"""
G-Counter (Grow-only Counter) CRDT implementation - File-based version
"""
from collections import defaultdict
from pathlib import Path
from ..base_crdt import BaseCRDT

class GCounter(BaseCRDT):
    """Grow-only Counter CRDT - tracks files as increment operations"""
    
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.counters = defaultdict(int)
        self.counters[node_id] = 0
        self.last_file_count = 0  # Track last known file count
        
    def increment(self, value=1):
        """Increment the counter manually"""
        if value > 0:
            self.counters[self.node_id] += value
            self.logger.info(f"Manually incremented by {value}. Local counter: {self.counters[self.node_id]}")
            return True
        return False
    
    def query(self):
        """Get the total counter value"""
        return sum(self.counters.values())
    
    def update_local_state(self):
        """Scan sync folder and treat each file as an increment operation"""
        try:
            current_file_count = 0
            for file_path in self.sync_folder.rglob('*'):
                if file_path.is_file():
                    current_file_count += 1
            
            # Calculate the difference since last scan
            if current_file_count > self.last_file_count:
                increment_amount = current_file_count - self.last_file_count
                self.counters[self.node_id] += increment_amount
                self.logger.info(f"Auto-incremented by {increment_amount} (files: {self.last_file_count} → {current_file_count}). Local counter: {self.counters[self.node_id]}")
                self.last_file_count = current_file_count
                return True
            elif current_file_count < self.last_file_count:
                # Files were deleted, but G-Counter can only grow
                self.logger.warning(f"Files decreased ({self.last_file_count} → {current_file_count}) but G-Counter cannot decrement")
                self.last_file_count = current_file_count
                return False
            else:
                # No change in file count
                return False
                
        except Exception as e:
            self.logger.error(f"Error scanning folder for G-Counter: {e}")
            return False
    
    def merge(self, other_state):
        """Merge another GCounter state"""
        merged = False
        for node_id, value in other_state['counters'].items():
            if value > self.counters[node_id]:
                self.logger.info(f"Updating counter for {node_id}: {self.counters[node_id]} → {value}")
                self.counters[node_id] = value
                merged = True
        
        if merged:
            total = self.query()
            self.logger.info(f"Merged GCounter state. New total: {total}")
        return merged
    
    def to_dict(self):
        return {
            'counters': dict(self.counters),
            'last_file_count': self.last_file_count
        }
    
    def from_dict(self, data):
        self.counters.clear()
        self.counters.update(data.get('counters', {}))
        self.last_file_count = data.get('last_file_count', 0)
        self.logger.info(f"Loaded GCounter state: {dict(self.counters)}, last_file_count: {self.last_file_count}")
    
    def get_state_summary(self):
        total = self.query()
        details = ", ".join([f"{node}: {count}" for node, count in self.counters.items()])
        current_files = sum(1 for _ in self.sync_folder.rglob('*') if _.is_file())
        return f"G-Counter Total: {total} (current files: {current_files}) [{details}]"
