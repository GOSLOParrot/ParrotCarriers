"""IntentWorkspace storage backend Protocol + baseline implementations.

BRAIN-INTENT-WS-V1 § 5.

InMemoryBackend is the desktop baseline (≤ 256 MB total; ≤ a few dozen
StagedRefs). DiskBackend is the alternative for larger payloads
(PHOTO / VIDEO_SHORT). Both implement the same Protocol so backends
can be swapped via ``register_intent_workspace_backend()``.

P3+ extensions (Redis / S3 / FAISS) plug in here without touching the
``IntentWorkspace`` upper API.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Protocol


# ─── Imports + types (lazy resolve to avoid circular) ─────────────


def _staged_ref_cls():
    from parrot.brain.intent_workspace import StagedRef  # noqa: WPS433
    return StagedRef


def _staged_ref_meta_cls():
    from parrot.brain.intent_workspace import StagedRefMetadata  # noqa: WPS433
    return StagedRefMetadata


def _payload_source_cls():
    from parrot.brain.intent_workspace import PayloadSource  # noqa: WPS433
    return PayloadSource


# ─── Protocol ────────────────────────────────────────────────────


class IntentWorkspaceBackend(Protocol):
    """Storage-backend contract; replaceable globally."""

    async def put(self, ref_id: str, payload: Any, metadata: Any) -> None: ...
    async def get(self, ref_id: str) -> Any: ...
    async def delete(self, ref_id: str) -> bool: ...
    def usage(self) -> int: ...
    def list_ref_ids(self) -> list[str]: ...
    async def close(self) -> None: ...


# ─── InMemoryBackend ─────────────────────────────────────────────


class InMemoryBackend:
    """Pure in-memory dict backend (desktop baseline)."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def put(self, ref_id: str, payload: Any, metadata: Any) -> None:
        StagedRef = _staged_ref_cls()
        self._store[ref_id] = StagedRef(
            ref_id=ref_id,
            kind=metadata.kind if hasattr(metadata, "kind") else None,
            payload_source=metadata.payload_source if hasattr(metadata, "payload_source") else None,
            payload=payload,
            metadata=metadata,
        )

    async def get(self, ref_id: str) -> Any:
        return self._store.get(ref_id)

    async def delete(self, ref_id: str) -> bool:
        return self._store.pop(ref_id, None) is not None

    def usage(self) -> int:
        total = 0
        for ref in self._store.values():
            payload = getattr(ref, "payload", None)
            if isinstance(payload, (bytes, bytearray)):
                total += len(payload)
            elif isinstance(payload, str):
                total += len(payload.encode("utf-8", "replace"))
            elif isinstance(payload, Path):
                try:
                    total += payload.stat().st_size
                except OSError:
                    total += 0
        return total

    def list_ref_ids(self) -> list[str]:
        return list(self._store.keys())

    async def close(self) -> None:
        self._store.clear()


# ─── DiskBackend ─────────────────────────────────────────────────


class DiskBackend:
    """Disk-backed payload store + in-memory metadata index.

    Payloads:
        - DISK_PATH      : symlink-style record (``payload`` is the
                           original Path; we don't copy the file)
        - INLINE_BYTES   : write to ``base/{ref_id}.bin``
        - INLINE_TEXT    : write to ``base/{ref_id}.txt`` (utf-8)
        - URL            : record url string in metadata file only

    # TODO(Chat4-disk-recover): SKELETON gap. ``.meta.json`` companion
    #   files are written but a ``recover()`` method that rebuilds
    #   ``self._index`` from disk on process start is NOT implemented.
    #   Chat 4 (or P3) must add:
    #     async def recover(self) -> int:
    #         '''Rescan ``self._base/*.meta.json`` and re-populate index.'''
    #   This is needed for crash-restart durability (currently restart
    #   loses all StagedRef metadata).
    """

    def __init__(self, base_path: Path | str = Path("data/intent_workspace")) -> None:
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, Any] = {}

    async def put(self, ref_id: str, payload: Any, metadata: Any) -> None:
        StagedRef = _staged_ref_cls()
        PayloadSource = _payload_source_cls()
        ps = getattr(metadata, "payload_source", None)
        stored_payload = payload

        if ps == PayloadSource.INLINE_BYTES and isinstance(payload, (bytes, bytearray)):
            target = self._base / f"{ref_id}.bin"
            await asyncio.to_thread(target.write_bytes, bytes(payload))
            stored_payload = target
        elif ps == PayloadSource.INLINE_TEXT and isinstance(payload, str):
            target = self._base / f"{ref_id}.txt"
            await asyncio.to_thread(target.write_text, payload, "utf-8")
            stored_payload = target
        # DISK_PATH and URL keep ``payload`` as-is.

        self._index[ref_id] = StagedRef(
            ref_id=ref_id,
            kind=getattr(metadata, "kind", None),
            payload_source=ps,
            payload=stored_payload,
            metadata=metadata,
        )

        # Write companion .meta.json for crash-recovery (P3 to consume)
        meta_path = self._base / f"{ref_id}.meta.json"
        try:
            await asyncio.to_thread(
                meta_path.write_text,
                json.dumps(
                    {
                        "ref_id": ref_id,
                        "kind": getattr(getattr(metadata, "kind", None), "value", None),
                        "payload_source": getattr(ps, "value", None),
                        "size_bytes": getattr(metadata, "size_bytes", 0),
                        "loaded_at": getattr(metadata, "loaded_at", time.time()),
                    },
                    ensure_ascii=False,
                ),
                "utf-8",
            )
        except OSError:
            pass

    async def get(self, ref_id: str) -> Any:
        return self._index.get(ref_id)

    async def delete(self, ref_id: str) -> bool:
        ref = self._index.pop(ref_id, None)
        if ref is None:
            return False
        for ext in (".bin", ".txt", ".meta.json"):
            target = self._base / f"{ref_id}{ext}"
            try:
                if target.exists():
                    target.unlink()
            except OSError:
                pass
        return True

    def usage(self) -> int:
        total = 0
        try:
            for child in self._base.iterdir():
                if child.is_file() and not child.name.endswith(".meta.json"):
                    try:
                        total += child.stat().st_size
                    except OSError:
                        pass
        except OSError:
            pass
        return total

    def list_ref_ids(self) -> list[str]:
        return list(self._index.keys())

    async def close(self) -> None:
        self._index.clear()


__all__ = [
    "DiskBackend",
    "InMemoryBackend",
    "IntentWorkspaceBackend",
]
