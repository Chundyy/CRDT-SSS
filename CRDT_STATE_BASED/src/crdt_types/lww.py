#!/usr/bin/env python3
"""
LWW (Last Writer Wins) File Sync CRDT
"""
from pathlib import Path
from datetime import datetime, timezone
from ..base_crdt import BaseCRDT
import os
import base64
import json
import tempfile
import time
from typing import Dict


class LWWFileSync(BaseCRDT):
    """Last Writer Wins CRDT for file synchronization"""

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.file_timestamps = {}  # rel_path -> iso timestamp
        self._state_file_name = '.lww_state.json'
        # load persisted tombstones/state if present
        try:
            self.load_state_file()
        except Exception:
            pass
        self.update_local_state()

    def _now_iso(self):
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def get_sync_path(self):
        sync_path = Path(self.sync_folder)
        if sync_path.name == 'lww':
            return sync_path
        return sync_path / 'lww'

    def update_local_state(self):
        """Scan sync folder and update file_timestamps with latest mtime.

        Preserve existing tombstones so deletions propagate. For current files update mtimes if newer.
        Record a tombstone (deletion timestamp) when a previously tracked file is missing.
        """
        scan_path = self.get_sync_path()
        # collect current files and mtimes
        current_files: Dict[str, str] = {}
        for file_path in scan_path.glob('**/*'):
            if file_path.is_file() and not file_path.name.startswith('.') and not file_path.name.endswith('.swp'):
                # normalize to posix-style relative path to avoid backslash issues across platforms
                rel_path = file_path.relative_to(scan_path).as_posix()
                ts = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc).isoformat().replace('+00:00', 'Z')
                current_files[rel_path] = ts

        # initialize from current files if no prior state
        if not self.file_timestamps:
            for rel, ts in current_files.items():
                self.file_timestamps[rel] = ts
            try:
                self.save_state_file()
            except Exception:
                pass
            return

        # update entries for current files if newer
        for rel, ts in current_files.items():
            existing = self.file_timestamps.get(rel)
            if existing is None or ts > existing:
                self.file_timestamps[rel] = ts

        # mark tombstones for previously tracked files that are now missing
        now_ts = self._now_iso()
        for rel in list(self.file_timestamps.keys()):
            file_path = scan_path / rel
            if not file_path.exists():
                existing = self.file_timestamps.get(rel)
                if existing is None or now_ts > existing:
                    self.file_timestamps[rel] = now_ts

        try:
            self.save_state_file()
        except Exception:
            pass

    def state_file_path(self) -> Path:
        return self.get_sync_path() / self._state_file_name

    def load_state_file(self):
        sf = self.state_file_path()
        if sf.exists():
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.file_timestamps = {str(k): str(v) for k, v in data.items()}
            except Exception as e:
                self.logger.warning(f"Failed to load LWW state file: {e}")

    def save_state_file(self):
        sf = self.state_file_path()
        sf.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(sf.parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(self.file_timestamps, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(sf))
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

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
                        try:
                            remote_content = base64.b64decode(remote_content)
                        except Exception as e:
                            self.logger.error(f"Failed to decode base64 content for {rel_path}: {e}")
                            # skip this entry
                            continue
                    elif isinstance(remote_content, (bytes, bytearray, memoryview)):
                        # convert memoryview to bytes
                        remote_content = bytes(remote_content)
                    else:
                        self.logger.warning(f"Unexpected remote_content type for {rel_path}: {type(remote_content)}")
                        continue
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
        if changed:
            try:
                self.save_state_file()
            except Exception:
                pass
        return changed

    def delete_file(self, rel_path: str) -> bool:
        """Record local deletion (tombstone) and remove local file if present."""
        try:
            scan_path = self.get_sync_path()
            file_path = scan_path / rel_path
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to remove local file during delete_file: {rel_path} - {e}")
            ts = self._now_iso()
            existing = self.file_timestamps.get(rel_path)
            if existing is None or ts > existing:
                self.file_timestamps[rel_path] = ts
                try:
                    self.save_state_file()
                except Exception:
                    pass
                self.logger.info(f"LWW LOCAL REMOVE: {rel_path} @ {ts}")
            return True
        except Exception as e:
            self.logger.error(f"delete_file failed for {rel_path}: {e}")
            return False

    def to_dict(self):
        """Export state as {rel_path: (timestamp, content)}"""
        scan_path = self.get_sync_path()
        state = {}
        for rel, ts in self.file_timestamps.items():
            # ensure consistent path handling
            file_path = scan_path / Path(rel)
            if file_path.exists():
                # attempt to read with retries to handle transient IO/lock issues (e.g., large files)
                content = None
                for attempt in range(3):
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        break
                    except Exception as e:
                        # brief backoff
                        time.sleep(0.1)
                        if attempt == 2:
                            # final failure
                            self.logger.error(f"Failed to read file for to_dict: {file_path} - {e}")
                if content is not None:
                    try:
                        # Encode bytes to base64 string for JSON serialization
                        content_str = base64.b64encode(content).decode('utf-8')
                        state[rel] = (ts, content_str)
                    except Exception as e:
                        self.logger.error(f"Failed to base64-encode file {file_path}: {e}")
                        state[rel] = (ts, None)
                else:
                    # Could not read file; keep timestamp but no content (will not overwrite remote newer content)
                    state[rel] = (ts, None)
            else:
                state[rel] = (ts, None)
        return state

    def from_dict(self, data):
        """Load state from {rel_path: (timestamp, content)}"""
        self.merge(data)

    def get_state_summary(self):
        return f"Tracked files: {len(self.file_timestamps)}"

