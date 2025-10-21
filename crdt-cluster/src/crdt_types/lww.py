#!/usr/bin/env python3
"""
Last-Writer-Wins (LWW) Element Set CRDT implementation.

This LWW set stores for each element a timestamp for the last add and the last remove
and resolves conflicts by choosing the operation with the most recent timestamp.
Elements are represented as relative file paths discovered under the configured
sync_folder, similar to other CRDTs in this project.
"""
from datetime import datetime, timezone
from pathlib import Path
from ..base_crdt import BaseCRDT
import os


class LWWElementSet(BaseCRDT):
    """LWW Element Set CRDT.

    Internal structure:
      - adds: dict[element] -> isotimestamp (string)
      - removes: dict[element] -> isotimestamp (string)

    An element is considered present if adds[element] > removes.get(element, "")
    (string ISO timestamps compare lexicographically and are sortable).
    """

    def __init__(self, node_id, sync_folder):
        super().__init__(node_id, sync_folder)
        self.adds = {}    # element -> iso timestamp
        self.removes = {} # element -> iso timestamp
        self.file_timestamps = {}  # element -> iso timestamp (conteúdo)

    def _now_iso(self):
        # use timezone-aware UTC timestamp (ISO) and normalize to Z
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def add(self, element, timestamp=None, content=None, content_timestamp=None):
        """Record an add for element with optional timestamp (now if None).
        Se content e content_timestamp forem dados, faz LWW ao conteúdo."""
        ts = timestamp or self._now_iso()
        prev = self.adds.get(element)
        updated = False
        if prev is None or ts > prev:
            self.adds[element] = ts
            self.logger.info(f"LWW ADD: {element} @ {ts}")
            updated = True
        else:
            self.logger.debug(f"Ignored older add for {element}: {ts} <= {prev}")
        # LWW para conteúdo
        if content is not None and content_timestamp is not None:
            prev_content_ts = self.file_timestamps.get(element)
            if prev_content_ts is None or content_timestamp > prev_content_ts:
                self._write_file_content(element, content)
                self.file_timestamps[element] = content_timestamp
                self.logger.info(f"LWW CONTENT: {element} @ {content_timestamp}")
                updated = True
        return updated

    def _write_file_content(self, element, content):
        """Escreve o conteúdo do ficheiro na pasta lww."""
        sync_path = self.get_lww_sync_path()
        file_path = sync_path / element
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(content)
        # Atualiza o mtime do ficheiro para o timestamp fornecido (opcional)

    def export_file_content(self, element):
        """Exporta o conteúdo e timestamp do ficheiro, se existir."""
        sync_path = self.get_lww_sync_path()
        file_path = sync_path / element
        if not file_path.exists():
            return None, None
        with open(file_path, 'rb') as f:
            content = f.read()
        ts = self.file_timestamps.get(element)
        if ts is None:
            ts = self._now_iso()
            self.file_timestamps[element] = ts
        return content, ts

    def is_present(self, element):
        """Return True if element is present in effective set."""
        a = self.adds.get(element)
        r = self.removes.get(element)
        if a is None:
            return False
        if r is None:
            return True
        return a > r

    def get_lww_sync_path(self):
        """Return the path to the LWW sync folder (sync_folder/lww)."""
        # Garantir que nunca duplica o 'lww' no caminho
        sync_path = self.sync_folder
        if sync_path.name == 'lww':
            return sync_path
        return sync_path / 'lww'

    def update_local_state(self):
        """Scan the sync_folder/lww directory and update the CRDT state accordingly."""
        try:
            scan_path = self.get_lww_sync_path()
            if not scan_path.exists():
                scan_path.mkdir(parents=True, exist_ok=True)
            current_files = set()

            for file in scan_path.glob('**/*'):
                if file.is_file():
                    rel_path = file.relative_to(scan_path)
                    current_files.add(str(rel_path))
                    # Atualiza o timestamp do conteúdo
                    ts = datetime.utcfromtimestamp(file.stat().st_mtime).replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
                    prev_ts = self.file_timestamps.get(str(rel_path))
                    if prev_ts is None or ts > prev_ts:
                        self.file_timestamps[str(rel_path)] = ts

            # Add newly found files
            for elem in current_files:
                if elem not in self.adds or not self.is_present(elem):
                    self.add(elem)

            # Mark removed files (those we knew about but are not on disk)
            known_elems = set(self.adds.keys()) | set(self.removes.keys())
            missing = {e for e in known_elems if e not in current_files and self.is_present(e)}
            for elem in missing:
                self.remove(elem)

            self.logger.info(f"LWW scan complete: found={len(current_files)} known={len(known_elems)} active={len(self.active_elements())}")
        except Exception as e:
            self.logger.error(f"Error during LWW scan: {e}")

    def merge(self, other_state):
        """Merge another node's state dict into this one.

        other_state expected keys: 'adds' and 'removes' mapping element->timestamp.
        For each element we keep the maximum timestamp per operation type.
        Returns True if this node's state changed.
        """
        changed = False
        other_adds = other_state.get('adds', {})
        other_removes = other_state.get('removes', {})

        # Merge adds
        for elem, ts in other_adds.items():
            local_ts = self.adds.get(elem)
            if local_ts is None or ts > local_ts:
                self.adds[elem] = ts
                changed = True
                self.logger.debug(f"Merged add {elem} @ {ts}")

        # Merge removes
        for elem, ts in other_removes.items():
            local_ts = self.removes.get(elem)
            if local_ts is None or ts > local_ts:
                self.removes[elem] = ts
                changed = True
                self.logger.debug(f"Merged remove {elem} @ {ts}")

        if changed:
            self.logger.info(f"LWW merge changed state. active={len(self.active_elements())}")
            self.apply_state_to_disk()
        return changed

    def to_dict(self):
        return {'adds': dict(self.adds), 'removes': dict(self.removes)}

    def from_dict(self, data):
        self.adds = dict(data.get('adds', {}))
        self.removes = dict(data.get('removes', {}))
        self.logger.info(f"Loaded LWW state: active={len(self.active_elements())} adds={len(self.adds)} removes={len(self.removes)}")

    def active_elements(self):
        """Return set of currently present elements."""
        return {e for e in self.adds.keys() if self.is_present(e)}

    def get_state_summary(self):
        active = len(self.active_elements())
        return f"LWW-Set: {active} active, {len(self.adds)} adds, {len(self.removes)} removes"

    def apply_state_to_disk(self):
        """Garante que todos os elementos ativos existem fisicamente em sync_folder/lww."""
        sync_path = self.get_lww_sync_path()
        for elem in self.active_elements():
            file_path = sync_path / elem
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
                self.logger.info(f"LWW: Criado ficheiro localmente após merge: {file_path}")
