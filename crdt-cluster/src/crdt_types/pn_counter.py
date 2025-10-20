#!/usr/bin/env python3
"""
PN-Counter (Positive-Negative Counter) CRDT implementation
"""
from collections import defaultdict
from ..base_crdt import BaseCRDT

class PNCounter(BaseCRDT):
    """Positive-Negative Counter CRDT - supports increment and decrement"""
    
    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.p_counters = defaultdict(int)  # Positive increments
        self.n_counters = defaultdict(int)  # Negative increments
        self.p_counters[node_id] = 0
        self.n_counters[node_id] = 0
        
    def increment(self, value=1):
        """Increment the counter"""
        if value > 0:
            self.p_counters[self.node_id] += value
            self.logger.info(f"Incremented by {value}")
            return True
        return False
    
    def decrement(self, value=1):
        """Decrement the counter"""
        if value > 0:
            self.n_counters[self.node_id] += value
            self.logger.info(f"Decremented by {value}")
            return True
        return False
    
    def query(self):
        """Get the total counter value"""
        pos = sum(self.p_counters.values())
        neg = sum(self.n_counters.values())
        return pos - neg
    
    def update_local_state(self):
        """PN-Counter doesn't scan files"""
        pass
    
    def merge(self, other_state):
        """Merge another PNCounter state"""
        merged = False
        for node_id, value in other_state['p_counters'].items():
            if value > self.p_counters[node_id]:
                self.p_counters[node_id] = value
                merged = True
        
        for node_id, value in other_state['n_counters'].items():
            if value > self.n_counters[node_id]:
                self.n_counters[node_id] = value
                merged = True
        
        if merged:
            self.logger.info("Merged PN-Counter state")
        return merged
    
    def to_dict(self):
        return {
            'p_counters': dict(self.p_counters),
            'n_counters': dict(self.n_counters)
        }
    
    def from_dict(self, data):
        self.p_counters.clear()
        self.n_counters.clear()
        self.p_counters.update(data.get('p_counters', {}))
        self.n_counters.update(data.get('n_counters', {}))
        self.logger.info("Loaded PN-Counter state from dict")
    
    def get_state_summary(self):
        total = self.query()
        pos = sum(self.p_counters.values())
        neg = sum(self.n_counters.values())
        return f"PN-Counter Total: {total} (Increments: {pos}, Decrements: {neg})"
