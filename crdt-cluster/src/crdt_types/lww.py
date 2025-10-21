#!/usr/bin/env python3
"""
Last Writer Wins (LWW) para sincronização de ficheiros.

Sincroniza ficheiros entre peers, mantendo sempre o conteúdo mais recente (pelo timestamp).
"""
from datetime import datetime, timezone
from pathlib import Path
from ..base_crdt import BaseCRDT
import os


class LWWFileSync(BaseCRDT):
    """
    Last Writer Wins (LWW) para sincronização de ficheiros.
    Sincroniza ficheiros entre peers, mantendo sempre o conteúdo mais recente (pelo timestamp).
    """

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.file_timestamps = {}  # rel_path -> iso timestamp

    def _now_iso(self):
        return datetime.fromtimestamp(datetime.now().timestamp(), timezone.utc).isoformat().replace('+00:00', 'Z')

    def get_sync_path(self):
        sync_path = Path(self.sync_folder)
        if sync_path.name == 'lww':
            return sync_path
        return sync_path / 'lww'

    def update_local_state(self):
        """
        Atualiza os timestamps de todos os ficheiros presentes na pasta de sync.
        """
        scan_path = self.get_sync_path()
        if not scan_path.exists():
            scan_path.mkdir(parents=True, exist_ok=True)
        for file in scan_path.glob('**/*'):
            if file.is_file():
                rel_path = str(file.relative_to(scan_path))
                ts = datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat().replace('+00:00', 'Z')
                prev_ts = self.file_timestamps.get(rel_path)
                if prev_ts is None or ts > prev_ts:
                    self.file_timestamps[rel_path] = ts

    def add_or_update_file(self, rel_path, content, timestamp=None):
        """
        Adiciona ou atualiza um ficheiro, apenas se o timestamp for mais recente.
        """
        ts = timestamp or self._now_iso()
        prev_ts = self.file_timestamps.get(rel_path)
        if prev_ts is None or ts > prev_ts:
            sync_path = self.get_sync_path()
            file_path = sync_path / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(content)
            self.file_timestamps[rel_path] = ts
            os.utime(file_path, (datetime.now().timestamp(), datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()))
            self.logger.info(f"LWW ADD/UPDATE: {rel_path} @ {ts}")
            return True
        self.logger.debug(f"Ignored older file for {rel_path}: {ts} <= {prev_ts}")
        return False

    def export_file(self, rel_path):
        """
        Exporta o conteúdo e timestamp do ficheiro, se existir.
        """
        sync_path = self.get_sync_path()
        file_path = sync_path / rel_path
        if not file_path.exists():
            return None, None
        with open(file_path, 'rb') as f:
            content = f.read()
        ts = self.file_timestamps.get(rel_path)
        if ts is None:
            ts = self._now_iso()
            self.file_timestamps[rel_path] = ts
        return content, ts

    def merge(self, other_state):
        """
        Recebe um dicionário {rel_path: (timestamp, content)} e aplica LWW ao conteúdo.
        """
        changed = False
        for rel_path, value in other_state.items():
            if not isinstance(value, tuple) or len(value) != 2:
                self.logger.error(f"Invalid state entry for {rel_path}: {value}")
                continue

            remote_ts, remote_content = value
            local_ts = self.file_timestamps.get(rel_path)
            if local_ts is None or remote_ts > local_ts:
                self.add_or_update_file(rel_path, remote_content, remote_ts)
                changed = True
        return changed

    def get_state(self):
        """
        Exporta o estado atual: {rel_path: (timestamp, content)}
        """
        state = {}
        sync_path = self.get_sync_path()
        for rel_path, ts in self.file_timestamps.items():
            file_path = sync_path / rel_path
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                state[rel_path] = (ts, content)
        return state

    def to_dict(self):
        """
        Convert the current state to a dictionary for serialization.
        """
        return {
            'file_timestamps': self.file_timestamps
        }

    def from_dict(self, data):
        """
        Load the state from a dictionary.
        """
        self.file_timestamps = data.get('file_timestamps', {})

    def get_state_summary(self):
        """
        Get a human-readable summary of the current state.
        """
        return f"Tracked files: {len(self.file_timestamps)}"