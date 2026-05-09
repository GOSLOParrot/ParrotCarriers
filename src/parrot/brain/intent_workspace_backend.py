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

    Crash recovery (NEED-P2.5 / formerly TODO(Chat4-disk-recover)):
        :meth:`recover` rescans ``self._base/*.meta.json`` and rebuilds
        :attr:`_index` without loading the actual payload bodies into
        memory. After recovery, large payloads remain on disk and only
        load lazily through :meth:`get` (which currently returns the
        ``StagedRef`` whose ``payload`` is a ``Path`` for INLINE_BYTES /
        INLINE_TEXT records — callers read the file themselves). This
        keeps recovery fast even with hundreds of staged photos.
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

        # Write companion .meta.json for crash-recovery (consumed by recover()).
        meta_path = self._base / f"{ref_id}.meta.json"
        try:
            url = payload if ps == _payload_source_cls().URL and isinstance(payload, str) else ""
            payload_meta = {
                "ref_id": ref_id,
                "kind": getattr(getattr(metadata, "kind", None), "value", None),
                "payload_source": getattr(ps, "value", None),
                "url": url,
                "origin": getattr(metadata, "origin", ""),
                "related_node_uuid": getattr(metadata, "related_node_uuid", ""),
                "related_intent_event_id": getattr(metadata, "related_intent_event_id", ""),
                "related_plan_id": getattr(metadata, "related_plan_id", ""),
                "size_bytes": getattr(metadata, "size_bytes", 0),
                "loaded_at": getattr(metadata, "loaded_at", time.time()),
                "last_accessed_at": getattr(metadata, "last_accessed_at", time.time()),
                "auto_evict_on_intent_close": bool(getattr(
                    metadata, "auto_evict_on_intent_close", True,
                )),
                "expires_at": getattr(metadata, "expires_at", 0.0),
                "custom_meta": dict(getattr(metadata, "custom_meta", {}) or {}),
            }
            await asyncio.to_thread(
                meta_path.write_text,
                json.dumps(payload_meta, ensure_ascii=False, default=str),
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

    # ─── Recovery ────────────────────────────────────────────────

    async def recover(self) -> list[tuple[str, Any]]:
        """Rebuild ``self._index`` from ``*.meta.json`` companion files.

        Returns a list of ``(ref_id, StagedRef)`` tuples so the caller
        (``IntentWorkspace.attach_disk_backend`` / startup) can re-populate
        upper-layer indexes (``_index`` + ``_idempotency``). Large payload
        files are NOT loaded into memory — only metadata is restored, and
        ``StagedRef.payload`` references the on-disk file path so the
        actual bytes load lazily on first ``fetch_payload`` call.

        Crash-resilient:
            - Skips unreadable / invalid .meta.json files.
            - Skips orphaned ``.bin`` / ``.txt`` without a meta sibling.
            - Idempotent: safe to call multiple times.
        """
        StagedRef = _staged_ref_cls()
        StagedRefMetadata = _staged_ref_meta_cls()
        PayloadSource = _payload_source_cls()

        recovered: list[tuple[str, Any]] = []
        try:
            meta_files = sorted(self._base.glob("*.meta.json"))
        except OSError:
            return recovered

        for meta_path in meta_files:
            ref_id = meta_path.stem.removesuffix(".meta")
            try:
                raw = await asyncio.to_thread(meta_path.read_text, "utf-8")
                obj = json.loads(raw)
            except (OSError, json.JSONDecodeError):
                continue

            ps_raw = obj.get("payload_source")
            kind_raw = obj.get("kind")

            try:
                ps = PayloadSource(ps_raw) if ps_raw else None
            except ValueError:
                ps = None

            # Lazy: import StagedRefKind here to keep the upper layer free
            # to evolve the enum without forcing this module to re-import.
            try:
                from parrot.brain.intent_workspace import StagedRefKind  # noqa: WPS433
                kind = StagedRefKind(kind_raw) if kind_raw else None
            except (ValueError, ImportError):
                kind = None

            payload_path: Any = None
            if ps == PayloadSource.INLINE_BYTES:
                cand = self._base / f"{ref_id}.bin"
                payload_path = cand if cand.exists() else None
            elif ps == PayloadSource.INLINE_TEXT:
                cand = self._base / f"{ref_id}.txt"
                payload_path = cand if cand.exists() else None
            elif ps == PayloadSource.DISK_PATH:
                # Original path was outside our base — meta only carries
                # metadata; the recover caller may re-stage if needed.
                payload_path = None
            elif ps == PayloadSource.URL:
                payload_path = obj.get("url")

            metadata = StagedRefMetadata(
                origin=obj.get("origin", "disk_recover"),
                kind=kind if kind else getattr(self, "_default_kind_sentinel", None),
                payload_source=ps,
                related_node_uuid=obj.get("related_node_uuid", ""),
                related_intent_event_id=obj.get("related_intent_event_id", ""),
                related_plan_id=obj.get("related_plan_id", ""),
                size_bytes=int(obj.get("size_bytes", 0)),
                loaded_at=float(obj.get("loaded_at", 0.0) or 0.0),
                last_accessed_at=float(obj.get("last_accessed_at", 0.0) or 0.0),
                auto_evict_on_intent_close=bool(obj.get("auto_evict_on_intent_close", True)),
                expires_at=float(obj.get("expires_at", 0.0) or 0.0),
                custom_meta=dict(obj.get("custom_meta") or {}),
            )

            ref = StagedRef(
                ref_id=ref_id,
                kind=kind,
                payload_source=ps,
                payload=payload_path,
                metadata=metadata,
            )
            self._index[ref_id] = ref
            recovered.append((ref_id, ref))

        return recovered


__all__ = [
    "DiskBackend",
    "InMemoryBackend",
    "IntentWorkspaceBackend",
]
