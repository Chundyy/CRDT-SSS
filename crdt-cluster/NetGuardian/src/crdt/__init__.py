"""
CRDT (Conflict-free Replicated Data Types) Module for NetGuardian

This module implements state-based CRDTs for distributed file management
with automatic conflict resolution and eventual consistency.

Components:
- crdt_manager: Core CRDT state management
- event_store: PostgreSQL-backed event sourcing
- lww_register: Last-Write-Wins Register implementation
- sync_engine: State synchronization engine
- vector_clock: Vector clock for causality tracking
"""

from .crdt_manager import CRDTManager
from .event_store import EventStore, Event
from .lww_register import LWWRegister
from .vector_clock import VectorClock
from .sync_engine import SyncEngine

__all__ = [
    'CRDTManager',
    'EventStore',
    'Event',
    'LWWRegister',
    'VectorClock',
    'SyncEngine'
]

__version__ = '1.0.0'
