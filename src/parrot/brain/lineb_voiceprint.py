"""Private owner-speaker verification support for LineB.

LineB needs two different audio judgements:

* echo detection: "is this recent agent TTS leaking back into the mic?"
* owner verification: "is this the enrolled user speaking?"

This module owns the second judgement. It deliberately keeps raw audio and
embeddings outside the repository. The repo stores only the contract, manifest
shape, and optional local verifier adapter.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ENV_ENABLED = "PARROT_LINEB_VOICEPRINT_ENABLED"
ENV_PROVIDER = "PARROT_LINEB_VOICEPRINT_PROVIDER"
ENV_PROFILE_ID = "PARROT_LINEB_VOICEPRINT_PROFILE_ID"
ENV_MANIFEST = "PARROT_LINEB_VOICEPRINT_MANIFEST"
ENV_ACCEPT = "PARROT_LINEB_VOICEPRINT_THRESHOLD_ACCEPT"
ENV_REJECT = "PARROT_LINEB_VOICEPRINT_THRESHOLD_REJECT"

DEFAULT_PROVIDER = "speechbrain_ecapa"
FAST_PROVIDER = "resemblyzer_fast"
DEFAULT_PROFILE_ID = "user_owner_default"
DEFAULT_ACCEPT_THRESHOLD = 0.78
DEFAULT_REJECT_THRESHOLD = 0.62
DEFAULT_SPEECHBRAIN_MODEL = "speechbrain/spkrec-ecapa-voxceleb"


@dataclass(frozen=True)
class VoiceprintRuntimeStatus:
    profile_id: str
    provider: str
    state: str
    health: str
    summary: str
    manifest_path: str = ""
    threshold_accept: float = DEFAULT_ACCEPT_THRESHOLD
    threshold_reject: float = DEFAULT_REJECT_THRESHOLD
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceprintVerification:
    profile_id: str
    provider: str
    decision: str
    speaker_role: str
    similarity: float
    threshold_accept: float
    threshold_reject: float
    reason: str
    observed_at: float = 0.0
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceprintEnrollmentResult:
    profile_id: str
    provider: str
    success: bool
    manifest_path: str
    positive_sample_count: int
    centroid_path: str
    embedding_index_path: str
    summary: str
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def runtime_status(
    *,
    env: Mapping[str, str] | None = None,
    enabled: bool | None = None,
    manifest_path: str | Path | None = None,
    provider: str = "",
    profile_id: str = "",
    threshold_accept: float | None = None,
    threshold_reject: float | None = None,
) -> VoiceprintRuntimeStatus:
    """Return whether LineB can verify an enrolled owner voice."""
    env = os.environ if env is None else env
    verifier_enabled = _truthy(env.get(ENV_ENABLED, "")) if enabled is None else bool(enabled)
    provider = _provider_key(_clean(provider or env.get(ENV_PROVIDER), DEFAULT_PROVIDER))
    profile_id = _clean(profile_id or env.get(ENV_PROFILE_ID), DEFAULT_PROFILE_ID)
    accept = _float_or_default(
        threshold_accept if threshold_accept is not None else env.get(ENV_ACCEPT),
        DEFAULT_ACCEPT_THRESHOLD,
    )
    reject = _float_or_default(
        threshold_reject if threshold_reject is not None else env.get(ENV_REJECT),
        DEFAULT_REJECT_THRESHOLD,
    )
    manifest_text = str(
        manifest_path if manifest_path is not None else env.get(ENV_MANIFEST, "")
    ).strip()
    if not verifier_enabled:
        return VoiceprintRuntimeStatus(
            profile_id=profile_id,
            provider=provider,
            state="disabled",
            health="warning",
            summary="LineB voiceprint verifier is disabled.",
            threshold_accept=accept,
            threshold_reject=reject,
        )
    if not manifest_text:
        return VoiceprintRuntimeStatus(
            profile_id=profile_id,
            provider=provider,
            state="not_configured",
            health="warning",
            summary="Voiceprint is enabled, but PARROT_LINEB_VOICEPRINT_MANIFEST is missing.",
            threshold_accept=accept,
            threshold_reject=reject,
        )
    manifest_ref = Path(manifest_text)

    manifest, load_error = _load_manifest(manifest_ref)
    if load_error:
        return VoiceprintRuntimeStatus(
            profile_id=profile_id,
            provider=provider,
            state="degraded",
            health="warning",
            summary=load_error,
            manifest_path=str(manifest_ref),
            threshold_accept=accept,
            threshold_reject=reject,
        )

    profile_id = _clean(manifest.get("profile_id"), profile_id)
    provider = _provider_key(_clean(_nested(manifest, "model", "provider"), provider))
    threshold_accept = _float_or_default(
        _nested(manifest, "thresholds", "accept_similarity"),
        accept,
    )
    threshold_reject = _float_or_default(
        _nested(manifest, "thresholds", "reject_similarity"),
        reject,
    )
    centroid, centroid_error = _load_centroid(manifest, manifest_ref)
    provider_ready = _provider_available(provider)
    if centroid_error:
        return VoiceprintRuntimeStatus(
            profile_id=profile_id,
            provider=provider,
            state="pending_enrollment",
            health="warning",
            summary=centroid_error,
            manifest_path=str(manifest_ref),
            threshold_accept=threshold_accept,
            threshold_reject=threshold_reject,
            refs={"provider_available": provider_ready},
        )
    if not provider_ready:
        return VoiceprintRuntimeStatus(
            profile_id=profile_id,
            provider=provider,
            state="degraded",
            health="warning",
            summary=(
                "Owner centroid exists, but the configured speaker verifier "
                "runtime is not importable on this machine."
            ),
            manifest_path=str(manifest_ref),
            threshold_accept=threshold_accept,
            threshold_reject=threshold_reject,
            refs={
                "centroid_dim": len(centroid),
                "provider_available": False,
            },
        )
    return VoiceprintRuntimeStatus(
        profile_id=profile_id,
        provider=provider,
        state="ready",
        health="ok",
        summary="LineB owner voiceprint verifier is enrolled and importable.",
        manifest_path=str(manifest_ref),
        threshold_accept=threshold_accept,
        threshold_reject=threshold_reject,
        refs={
            "centroid_dim": len(centroid),
            "provider_available": True,
        },
    )


def verify_embedding(
    embedding: Sequence[float],
    *,
    env: Mapping[str, str] | None = None,
    enabled: bool | None = None,
    manifest_path: str | Path | None = None,
    provider: str = "",
    profile_id: str = "",
    threshold_accept: float | None = None,
    threshold_reject: float | None = None,
    observed_at: float | None = None,
) -> VoiceprintVerification:
    """Verify one already-extracted speaker embedding against the owner centroid."""
    env = os.environ if env is None else env
    status = runtime_status(
        env=env,
        enabled=enabled,
        manifest_path=manifest_path,
        provider=provider,
        profile_id=profile_id,
        threshold_accept=threshold_accept,
        threshold_reject=threshold_reject,
    )
    observed = time.time() if observed_at is None else _float_or_default(observed_at, time.time())
    if status.state in {"disabled", "not_configured"}:
        return VoiceprintVerification(
            profile_id=status.profile_id,
            provider=status.provider,
            decision=status.state,
            speaker_role="unknown",
            similarity=0.0,
            threshold_accept=status.threshold_accept,
            threshold_reject=status.threshold_reject,
            reason=status.summary,
            observed_at=observed,
            refs=status.as_json(),
        )

    manifest, load_error = _load_manifest(Path(status.manifest_path))
    if load_error:
        return _verification_error(status, "manifest_error", load_error, observed)
    centroid, centroid_error = _load_centroid(manifest, Path(status.manifest_path))
    if centroid_error:
        return _verification_error(status, "not_enrolled", centroid_error, observed)

    similarity = _cosine_similarity(_vector(embedding), centroid)
    if similarity >= status.threshold_accept:
        decision = "owner_user"
        speaker_role = "user"
        reason = "speaker_similarity_accept"
    elif similarity <= status.threshold_reject:
        decision = "other_speaker"
        speaker_role = "other"
        reason = "speaker_similarity_reject"
    else:
        decision = "uncertain"
        speaker_role = "uncertain"
        reason = "speaker_similarity_between_thresholds"

    return VoiceprintVerification(
        profile_id=status.profile_id,
        provider=status.provider,
        decision=decision,
        speaker_role=speaker_role,
        similarity=round(similarity, 4),
        threshold_accept=status.threshold_accept,
        threshold_reject=status.threshold_reject,
        reason=reason,
        observed_at=observed,
        refs={
            "manifest_path": status.manifest_path,
            "centroid_dim": len(centroid),
            "embedding_dim": len(_vector(embedding)),
        },
    )


def verify_audio_file(
    audio_path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
    manifest_path: str | Path | None = None,
    observed_at: float | None = None,
) -> VoiceprintVerification:
    """Extract a speaker embedding from a private audio file and verify it.

    This requires optional dependencies from ``parrotcarriers[voiceprint]`` and
    should run on ECS/private storage, not inside the Git repository.
    """
    embedding = extract_embedding_from_audio(audio_path, env=env)
    return verify_embedding(
        embedding,
        env=env,
        manifest_path=manifest_path,
        observed_at=observed_at,
    )


def enroll_from_audio_files(
    audio_paths: Iterable[str | Path],
    *,
    manifest_path: str | Path,
    env: Mapping[str, str] | None = None,
    profile_id: str | None = None,
) -> VoiceprintEnrollmentResult:
    """Enroll an owner profile from private audio files.

    The function writes JSON feature files next to the manifest so Cursor/ECS
    can inspect them without requiring NumPy. It does not touch the repository.
    """
    manifest_ref = Path(manifest_path)
    manifest_ref.parent.mkdir(parents=True, exist_ok=True)
    manifest, _load_error = _load_manifest(manifest_ref)
    env = os.environ if env is None else env
    provider = _provider_key(_clean(
        _nested(manifest, "model", "provider") or env.get(ENV_PROVIDER),
        DEFAULT_PROVIDER,
    ))
    resolved_profile_id = _clean(
        profile_id or manifest.get("profile_id") or env.get(ENV_PROFILE_ID),
        DEFAULT_PROFILE_ID,
    )

    embeddings: list[list[float]] = []
    used_paths: list[str] = []
    for path in audio_paths:
        resolved = Path(path)
        embedding = extract_embedding_from_audio(resolved, env=env)
        embeddings.append(_vector(embedding))
        used_paths.append(str(resolved))
    if not embeddings:
        return VoiceprintEnrollmentResult(
            profile_id=resolved_profile_id,
            provider=provider,
            success=False,
            manifest_path=str(manifest_ref),
            positive_sample_count=0,
            centroid_path="",
            embedding_index_path="",
            summary="No enrollment audio files were provided.",
        )

    centroid = _mean_vector(embeddings)
    feature_root = Path(
        _nested(manifest, "storage", "feature_root")
        or manifest_ref.parent / "features"
    )
    feature_root.mkdir(parents=True, exist_ok=True)
    centroid_path = feature_root / "owner_centroid.json"
    embedding_index_path = feature_root / "enroll_embeddings.json"
    centroid_path.write_text(json.dumps(centroid, indent=2), encoding="utf-8")
    embedding_index_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": resolved_profile_id,
                "provider": provider,
                "samples": [
                    {"path": path, "embedding": embedding}
                    for path, embedding in zip(used_paths, embeddings, strict=False)
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    updated = dict(manifest)
    updated["schema_version"] = int(updated.get("schema_version") or 1)
    updated["profile_id"] = resolved_profile_id
    updated.setdefault("model", {})["provider"] = provider
    updated.setdefault("model", {})["model_id"] = (
        _nested(updated, "model", "model_id") or DEFAULT_SPEECHBRAIN_MODEL
    )
    updated.setdefault("enrollment", {})["positive_sample_count"] = len(embeddings)
    updated["enrollment"]["centroid_path"] = str(centroid_path)
    updated["enrollment"]["embedding_index_path"] = str(embedding_index_path)
    updated.setdefault("thresholds", {})["accept_similarity"] = _float_or_default(
        _nested(updated, "thresholds", "accept_similarity"),
        DEFAULT_ACCEPT_THRESHOLD,
    )
    updated["thresholds"]["reject_similarity"] = _float_or_default(
        _nested(updated, "thresholds", "reject_similarity"),
        DEFAULT_REJECT_THRESHOLD,
    )
    manifest_ref.write_text(json.dumps(updated, indent=2), encoding="utf-8")

    return VoiceprintEnrollmentResult(
        profile_id=resolved_profile_id,
        provider=provider,
        success=True,
        manifest_path=str(manifest_ref),
        positive_sample_count=len(embeddings),
        centroid_path=str(centroid_path),
        embedding_index_path=str(embedding_index_path),
        summary="Owner voiceprint enrollment files were written to private storage.",
        refs={"audio_paths": used_paths},
    )


def extract_embedding_from_audio(
    audio_path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
) -> list[float]:
    """Extract a speaker embedding with SpeechBrain ECAPA when installed."""
    env = os.environ if env is None else env
    provider = _provider_key(_clean(env.get(ENV_PROVIDER), DEFAULT_PROVIDER))
    if provider == FAST_PROVIDER:
        return _extract_resemblyzer_embedding(audio_path)
    if provider != DEFAULT_PROVIDER:
        raise RuntimeError(f"unsupported voiceprint provider: {provider}")
    try:
        import torch
        import torchaudio
    except ImportError as exc:  # pragma: no cover - optional runtime path.
        raise RuntimeError(
            "voiceprint audio extraction needs parrotcarriers[voiceprint] "
            "(torch, torchaudio, speechbrain)."
        ) from exc

    try:  # pragma: no cover - optional runtime path.
        from speechbrain.inference.speaker import EncoderClassifier
    except ImportError:  # pragma: no cover - SpeechBrain < 1.0 compatibility.
        from speechbrain.pretrained import EncoderClassifier  # type: ignore

    audio_ref = Path(audio_path)
    if not audio_ref.is_file():
        raise FileNotFoundError(str(audio_ref))

    signal, sample_rate = torchaudio.load(str(audio_ref))
    if signal.shape[0] > 1:
        signal = signal.mean(dim=0, keepdim=True)
    if int(sample_rate) != 16000:
        signal = torchaudio.transforms.Resample(sample_rate, 16000)(signal)
    model_id = env.get("PARROT_LINEB_VOICEPRINT_MODEL_ID", DEFAULT_SPEECHBRAIN_MODEL)
    savedir = env.get(
        "PARROT_LINEB_VOICEPRINT_MODEL_CACHE",
        str(Path.home() / ".cache" / "parrotcarriers" / "voiceprint" / "ecapa"),
    )
    classifier = EncoderClassifier.from_hparams(source=model_id, savedir=savedir)
    with torch.no_grad():
        embedding = classifier.encode_batch(signal).squeeze().detach().cpu().tolist()
    return _vector(embedding)


def decision_payload_for_similarity(
    similarity: float | None,
    *,
    env: Mapping[str, str] | None = None,
    enabled: bool | None = None,
    manifest_path: str | Path | None = None,
    provider: str = "",
    profile_id: str = "",
    threshold_accept: float | None = None,
    threshold_reject: float | None = None,
) -> dict[str, Any]:
    """Convert a precomputed similarity score into the same decision schema."""
    env = os.environ if env is None else env
    status = runtime_status(
        env=env,
        enabled=enabled,
        manifest_path=manifest_path,
        provider=provider,
        profile_id=profile_id,
        threshold_accept=threshold_accept,
        threshold_reject=threshold_reject,
    )
    if similarity is None:
        return VoiceprintVerification(
            profile_id=status.profile_id,
            provider=status.provider,
            decision="not_measured",
            speaker_role="unknown",
            similarity=0.0,
            threshold_accept=status.threshold_accept,
            threshold_reject=status.threshold_reject,
            reason="speaker_similarity_missing",
            observed_at=time.time(),
            refs=status.as_json(),
        ).as_json()
    value = max(-1.0, min(1.0, _float_or_default(similarity, 0.0)))
    if status.state in {"disabled", "not_configured", "pending_enrollment"}:
        return VoiceprintVerification(
            profile_id=status.profile_id,
            provider=status.provider,
            decision=status.state,
            speaker_role="unknown",
            similarity=round(value, 4),
            threshold_accept=status.threshold_accept,
            threshold_reject=status.threshold_reject,
            reason=status.summary,
            observed_at=time.time(),
            refs=status.as_json(),
        ).as_json()
    if value >= status.threshold_accept:
        decision, speaker_role, reason = (
            "owner_user",
            "user",
            "speaker_similarity_accept",
        )
    elif value <= status.threshold_reject:
        decision, speaker_role, reason = (
            "other_speaker",
            "other",
            "speaker_similarity_reject",
        )
    else:
        decision, speaker_role, reason = (
            "uncertain",
            "uncertain",
            "speaker_similarity_between_thresholds",
        )
    return VoiceprintVerification(
        profile_id=status.profile_id,
        provider=status.provider,
        decision=decision,
        speaker_role=speaker_role,
        similarity=round(value, 4),
        threshold_accept=status.threshold_accept,
        threshold_reject=status.threshold_reject,
        reason=reason,
        observed_at=time.time(),
        refs=status.as_json(),
    ).as_json()


def _verification_error(
    status: VoiceprintRuntimeStatus,
    decision: str,
    reason: str,
    observed_at: float,
) -> VoiceprintVerification:
    return VoiceprintVerification(
        profile_id=status.profile_id,
        provider=status.provider,
        decision=decision,
        speaker_role="unknown",
        similarity=0.0,
        threshold_accept=status.threshold_accept,
        threshold_reject=status.threshold_reject,
        reason=reason,
        observed_at=observed_at,
        refs=status.as_json(),
    )


def _load_manifest(path: Path) -> tuple[dict[str, Any], str]:
    if not str(path):
        return {}, "voiceprint manifest path is empty."
    try:
        if not path.is_file():
            return {}, f"voiceprint manifest does not exist: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"voiceprint manifest is unreadable: {exc}"
    if not isinstance(data, dict):
        return {}, "voiceprint manifest must be a JSON object."
    return data, ""


def _load_centroid(
    manifest: Mapping[str, Any],
    manifest_path: Path,
) -> tuple[list[float], str]:
    inline = (
        _nested(manifest, "enrollment", "centroid")
        or _nested(manifest, "enrollment", "centroid_vector")
        or _nested(manifest, "verification", "centroid")
    )
    if isinstance(inline, Sequence) and not isinstance(inline, (str, bytes)):
        vector = _vector(inline)
        return (vector, "") if vector else ([], "inline owner centroid is empty.")

    centroid_path = str(_nested(manifest, "enrollment", "centroid_path") or "").strip()
    if not centroid_path:
        return [], "voiceprint owner centroid is missing; run enrollment first."
    path = Path(centroid_path)
    if not path.is_absolute():
        path = manifest_path.parent / path
    if not path.is_file():
        return [], f"voiceprint owner centroid file does not exist: {path}"
    try:
        if path.suffix.lower() == ".npy":
            try:
                import numpy as np
            except ImportError as exc:
                return [], f"NumPy is required to read centroid file {path}: {exc}"
            data = np.load(path)
            return _vector(data.reshape(-1).tolist()), ""
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [], f"voiceprint owner centroid file is unreadable: {exc}"
    if isinstance(loaded, Mapping):
        loaded = loaded.get("centroid") or loaded.get("embedding") or loaded.get("vector")
    vector = _vector(loaded if isinstance(loaded, Sequence) else [])
    return (vector, "") if vector else ([], "voiceprint owner centroid file is empty.")


def _provider_available(provider: str) -> bool:
    provider = _provider_key(provider)
    if provider == DEFAULT_PROVIDER:
        return (
            importlib.util.find_spec("speechbrain") is not None
            and importlib.util.find_spec("torch") is not None
            and importlib.util.find_spec("torchaudio") is not None
        )
    if provider == FAST_PROVIDER:
        return importlib.util.find_spec("resemblyzer") is not None
    if provider in {"precomputed", "external"}:
        return True
    return False


def _provider_key(provider: str) -> str:
    key = str(provider or "").strip().lower()
    if key in {"speechbrain", "speechbrain_ecapa", "speechbrain-ecapa"}:
        return DEFAULT_PROVIDER
    if key in {"resemblyzer", "resemblyzer_fast", "resemblyzer-fast"}:
        return FAST_PROVIDER
    return key


def _extract_resemblyzer_embedding(audio_path: str | Path) -> list[float]:
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
    except ImportError as exc:  # pragma: no cover - optional runtime path.
        raise RuntimeError(
            "resemblyzer_fast extraction needs parrotcarriers[voiceprint_fast]."
        ) from exc
    audio_ref = Path(audio_path)
    if not audio_ref.is_file():
        raise FileNotFoundError(str(audio_ref))
    wav = preprocess_wav(audio_ref)
    embedding = VoiceEncoder().embed_utterance(wav)
    return _vector(embedding.tolist() if hasattr(embedding, "tolist") else embedding)


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    size = min(len(left), len(right))
    if size <= 0:
        return 0.0
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for idx in range(size):
        a = float(left[idx])
        b = float(right[idx])
        dot += a * b
        left_norm += a * a
        right_norm += b * b
    if left_norm <= 0.0 or right_norm <= 0.0:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)


def _mean_vector(vectors: Sequence[Sequence[float]]) -> list[float]:
    if not vectors:
        return []
    size = min(len(v) for v in vectors)
    if size <= 0:
        return []
    return [
        sum(float(vector[idx]) for vector in vectors) / len(vectors)
        for idx in range(size)
    ]


def _vector(value: Any) -> list[float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return []
    out: list[float] = []
    for item in value:
        parsed = _float_or_default(item, math.nan)
        if math.isfinite(parsed):
            out.append(parsed)
    return out


def _nested(data: Mapping[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _clean(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _float_or_default(value: Any, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


__all__ = [
    "DEFAULT_PROVIDER",
    "VoiceprintEnrollmentResult",
    "VoiceprintRuntimeStatus",
    "VoiceprintVerification",
    "decision_payload_for_similarity",
    "enroll_from_audio_files",
    "extract_embedding_from_audio",
    "runtime_status",
    "verify_audio_file",
    "verify_embedding",
]
