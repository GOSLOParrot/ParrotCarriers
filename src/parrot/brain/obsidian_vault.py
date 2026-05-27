"""Local Obsidian vault readiness checks for GOSLO App v1.

The first App version treats Obsidian as a local user-owned vault. Daily and
roleplay notes are setting sources and can be identified by path/title. Ref
notes are binding/strengthening sources and normally carry an Obsidian UUID.
Operator import paths may explicitly lift UUID-free ref diary notes as direct
context instead of RefBinding targets.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VaultCheckResult:
    """Compact report for CLI, menu canvas, or a smoke dashboard."""

    status: str
    vault_path: str
    markdown_count: int
    ingest_ready_count: int
    invalid_count: int
    profile_counts: dict[str, int]
    sample_ready_notes: list[dict[str, Any]]
    sample_invalid_notes: list[str]
    recommendation: str


def parse_simple_frontmatter(path: Path) -> tuple[dict[str, str], str] | None:
    """Parse a small YAML-like frontmatter block without adding dependencies."""
    # Windows editors and some Obsidian/plugin export paths may leave a UTF-8
    # BOM at the start of a Markdown file. Treat it as transport noise so a
    # valid frontmatter block still scans as import-ready.
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None

    raw_frontmatter = text[3:end].strip()
    body = text[end + 4 :].strip()
    meta: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def collect_markdown_files(vault_path: Path) -> list[Path]:
    """Collect user Markdown notes, skipping Obsidian app config files."""
    vault = Path(vault_path)
    if vault.is_file() and vault.suffix.lower() == ".md":
        return [vault]
    files = []
    for path in sorted(vault.rglob("*.md")):
        if ".obsidian" not in path.parts:
            files.append(path)
    return files


def normalize_profile(raw: object) -> str:
    """Normalize Obsidian profile aliases used by the app design."""
    value = str(raw or "daily").strip().lower().replace("-", "_")
    aliases = {
        "setting": "daily",
        "setting_daily": "daily",
        "daily_setting": "daily",
        "setting_roleplay": "roleplay",
        "roleplay_setting": "roleplay",
        "rp": "roleplay",
        "reference": "ref",
        "ref_reinforce": "ref",
    }
    return aliases.get(value, value)


def note_identity(meta: dict[str, str], path: Path) -> str:
    """Return the stable identity used for provenance in App v1."""
    return meta.get("uuid") or meta.get("obsidian_uuid") or str(path)


def note_to_ingest_payload(
    path: Path,
    *,
    allow_uuid_free_ref: bool = False,
) -> dict[str, Any] | None:
    """Convert one note to the payload consumed by ObsidianIngestTrigger.

    Returns None when the note should not enter GOSLO memory.
    """
    parsed = parse_simple_frontmatter(path)
    if parsed is None:
        return None

    meta, body = parsed
    profile = normalize_profile(meta.get("profile", "daily"))
    uuid = meta.get("uuid") or meta.get("obsidian_uuid") or ""
    if profile == "ref" and not uuid:
        if not allow_uuid_free_ref:
            return None
        ref_mode = "direct_context"
    else:
        ref_mode = str(meta.get("ref_mode") or "").strip()

    label = meta.get("label") or meta.get("title") or path.stem
    tags = _list_value(meta.get("tags"))
    for key in ("category", "material", "usual_location", "color", "owner"):
        if meta.get(key):
            tags.append(f"{key}:{meta[key]}")

    kind = meta.get("kind", "object") or "object"
    if profile == "ref" and not uuid and ref_mode == "direct_context":
        kind = meta.get("kind") or "event"

    payload = {
        "type": "obsidian_note",
        "label": label,
        "obsidian_uuid": uuid,
        "obsidian_note_key": note_identity(meta, path),
        "profile": profile,
        "kind": kind,
        "description": (meta.get("description") or body or "")[:400],
        "tags": tags[:10],
        "obsidian_path": str(path),
        "file_mtime": path.stat().st_mtime,
        "double_link_count": path.read_text(encoding="utf-8").count("[["),
        "target_node_uuid": meta.get("target_node_uuid", "") or "",
        "graphiti_uuid": meta.get("graphiti_uuid", "") or "",
    }
    if ref_mode:
        payload["ref_mode"] = ref_mode
    if profile == "ref" and not uuid and ref_mode == "direct_context":
        payload["context_role"] = "obsidian_ref_diary_context"
        payload["ascent_channel"] = "intent_workspace_doc+c3_context_notice"
    return payload


def check_obsidian_vault(
    vault_path: Path,
    sample_limit: int = 5,
    *,
    allow_uuid_free_ref: bool = False,
) -> VaultCheckResult:
    """Scan a vault and classify whether it can feed the Obsidian bridge."""
    vault = Path(vault_path).expanduser().resolve()
    if not vault.exists():
        return VaultCheckResult(
            status="missing_path",
            vault_path=str(vault),
            markdown_count=0,
            ingest_ready_count=0,
            invalid_count=0,
            profile_counts={},
            sample_ready_notes=[],
            sample_invalid_notes=[],
            recommendation="Create the vault locally or pass the correct vault directory.",
        )

    md_files = collect_markdown_files(vault)
    profile_counts: Counter[str] = Counter()
    ready_samples: list[dict[str, Any]] = []
    invalid_samples: list[str] = []
    ready_count = 0

    for md_file in md_files:
        payload = note_to_ingest_payload(
            md_file,
            allow_uuid_free_ref=allow_uuid_free_ref,
        )
        if payload is None:
            if len(invalid_samples) < sample_limit:
                invalid_samples.append(_relative_or_name(md_file, vault))
            continue

        profile = str(payload["profile"])
        profile_counts[profile] += 1
        ready_count += 1
        if len(ready_samples) < sample_limit:
            ready_samples.append({
                "label": payload.get("label", ""),
                "profile": profile,
                "obsidian_uuid": payload.get("obsidian_uuid", ""),
                "path": _relative_or_name(md_file, vault),
            })

    invalid_count = len(md_files) - ready_count
    if not md_files:
        status = "reachable_empty"
        recommendation = "Add Markdown notes to the vault before syncing."
    elif ready_count == 0:
        status = "reachable_not_ingest_ready"
        recommendation = (
            "Add profile/title frontmatter. Daily/roleplay notes do not need "
            "uuid; ref notes do."
        )
    else:
        status = "ingest_ready"
        recommendation = (
            "Run sync_obsidian_to_graphiti.py --dry-run first, then remove "
            "--dry-run when the Brain/Redis runtime is available."
        )

    return VaultCheckResult(
        status=status,
        vault_path=str(vault),
        markdown_count=len(md_files),
        ingest_ready_count=ready_count,
        invalid_count=invalid_count,
        profile_counts=dict(sorted(profile_counts.items())),
        sample_ready_notes=ready_samples,
        sample_invalid_notes=invalid_samples,
        recommendation=recommendation,
    )


def _list_value(raw: str | None) -> list[str]:
    """Parse comma-separated frontmatter list values."""
    if not raw:
        return []
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def _relative_or_name(path: Path, root: Path) -> str:
    """Render a stable local path for UI/debug status."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name


__all__ = [
    "VaultCheckResult",
    "check_obsidian_vault",
    "collect_markdown_files",
    "normalize_profile",
    "note_to_ingest_payload",
    "parse_simple_frontmatter",
]
