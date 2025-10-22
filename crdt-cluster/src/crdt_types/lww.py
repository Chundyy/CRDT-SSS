#!/usr/bin/env python3
"""
LWW (Last Writer Wins) File Sync CRDT
"""
from pathlib import Path
from datetime import datetime, timezone
from ..base_crdt import BaseCRDT
import os
import base64


class LWWFileSync(BaseCRDT):
    """Last Writer Wins CRDT for file synchronization"""

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.file_timestamps = {}  # rel_path -> iso timestamp
        self.update_local_state()

    def _now_iso(self):
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def get_sync_path(self):
        sync_path = Path(self.sync_folder)
        if sync_path.name == 'lww':
            return sync_path
        return sync_path / 'lww'

    def update_local_state(self):
        """Scan sync folder and update file_timestamps with latest mtime."""
        scan_path = self.get_sync_path()
        self.file_timestamps = {}
        for file_path in scan_path.glob('**/*'):
            if file_path.is_file() and not file_path.name.startswith('.') and not file_path.name.endswith('.swp'):
                rel_path = str(file_path.relative_to(scan_path))
                ts = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc).isoformat().replace('+00:00', 'Z')
                self.file_timestamps[rel_path] = ts

    def merge(self, other_state):
        """Merge state from another node. State: {rel_path: (timestamp, content)}"""
        changed = False
        scan_path = self.get_sync_path()
        for rel_path, (remote_ts, remote_content) in other_state.items():
            if rel_path.startswith('.') or rel_path.endswith('.swp'):
                continue
            local_ts = self.file_timestamps.get(rel_path)
            if local_ts is None or remote_ts > local_ts:
                file_path = scan_path / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if remote_content is not None:
                    # Decode base64 string to bytes if needed
                    if isinstance(remote_content, str):
                        remote_content = base64.b64decode(remote_content)
                    with open(file_path, 'wb') as f:
                        f.write(remote_content)
                    self.file_timestamps[rel_path] = remote_ts
                    self.logger.info(f"LWW ADD/UPDATE: {rel_path} @ {remote_ts}")
                else:
                    if file_path.exists():
                        file_path.unlink()
                    self.file_timestamps[rel_path] = remote_ts
                    self.logger.info(f"LWW REMOVE: {rel_path} @ {remote_ts}")
                changed = True
        return changed

    def to_dict(self):
        """Export state as {rel_path: (timestamp, content)}"""
        scan_path = self.get_sync_path()
        state = {}
        for rel_path, ts in self.file_timestamps.items():
            file_path = scan_path / rel_path
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                # Encode bytes to base64 string for JSON serialization
                content_str = base64.b64encode(content).decode('utf-8')
                state[rel_path] = (ts, content_str)
            else:
                state[rel_path] = (ts, None)
        return state

    def from_dict(self, data):
        """Load state from {rel_path: (timestamp, content)}"""
        self.merge(data)

    def get_state_summary(self):
        return f"Tracked files: {len(self.file_timestamps)}"