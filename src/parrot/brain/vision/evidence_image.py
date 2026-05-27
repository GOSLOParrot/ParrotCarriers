"""Stored-image helpers for time-aligned evidence.

ECP/RPC events should carry evidence ids and timebase metadata, not image
bytes.  This module is the narrow Brain-side bridge that dereferences a stored
asset, applies an optional evidence region, and prepares bytes for VLM tools.
"""

from __future__ import annotations

import base64
import hashlib
import io
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from parrot.brain.vision.evidence import SampleRegion, TimeAlignedSampleRef


@dataclass(slots=True, frozen=True)
class PreparedEvidenceImage:
    """A local evidence image prepared for VLM input."""

    b64_jpeg: str
    width: int
    height: int
    cropped: bool
    asset_path: str


@dataclass(slots=True, frozen=True)
class PersistedEvidenceCrop:
    """A local crop/reference image written to disk for object samples."""

    crop_path: str
    width: int
    height: int
    cropped: bool
    source_asset_path: str
    content_sha256: str


def prepare_evidence_image(
    sample: "TimeAlignedSampleRef",
    *,
    max_dimension: int = 960,
) -> PreparedEvidenceImage | None:
    """Load and optionally crop a stored evidence image.

    Only local storage assets are supported in V1.  ``asset_uri`` is kept in the
    evidence model for future HTTP/storage dereferencing, but this helper avoids
    hidden network fetches inside the synchronous ``identify_object`` budget.
    """
    path_text = str(getattr(sample, "asset_path", "") or "")
    if not path_text:
        return None
    path = Path(path_text)
    if not path.is_file():
        return None

    with Image.open(path) as opened:
        image = opened.convert("RGB")
    cropped = False
    region = getattr(sample, "region", None)
    if region is not None:
        next_image = _crop_region(image, region)
        if next_image is not image:
            image = next_image
            cropped = True

    if max_dimension and max(image.size) > max_dimension:
        scale = max_dimension / float(max(image.size))
        resized = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
        image = image.resize(resized, resample)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=82)
    return PreparedEvidenceImage(
        b64_jpeg=base64.b64encode(output.getvalue()).decode("ascii"),
        width=image.width,
        height=image.height,
        cropped=cropped,
        asset_path=str(path),
    )


def persist_evidence_crop(
    sample: "TimeAlignedSampleRef",
    output_path: str | Path,
    *,
    max_dimension: int = 0,
    assume_source_is_crop: bool = False,
) -> PersistedEvidenceCrop | None:
    """Persist a sample image or its region crop to ``output_path``.

    The caller decides whether the source asset is already a region capture.
    This matters for App BBox/MAG assets, where Unity often uploads the
    selected screen region directly; cropping those a second time would lose
    the user's chosen pixels.
    """
    path_text = str(getattr(sample, "asset_path", "") or "")
    if not path_text:
        return None
    path = Path(path_text)
    if not path.is_file():
        return None

    with Image.open(path) as opened:
        image = opened.convert("RGB")
    cropped = False
    region = getattr(sample, "region", None)
    if region is not None and not assume_source_is_crop:
        next_image = _crop_region(image, region)
        if next_image is not image:
            image = next_image
            cropped = True

    if max_dimension and max(image.size) > max_dimension:
        scale = max_dimension / float(max(image.size))
        resized = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
        image = image.resize(resized, resample)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="JPEG", quality=88)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return PersistedEvidenceCrop(
        crop_path=str(output),
        width=image.width,
        height=image.height,
        cropped=cropped,
        source_asset_path=str(path),
        content_sha256=digest,
    )


async def describe_evidence_sample(sample: "TimeAlignedSampleRef") -> str:
    """Describe a stored evidence image through the existing VLM helper."""
    prepared = prepare_evidence_image(sample)
    if prepared is None:
        return ""

    from parrot.brain.vision.visual_match import describe_image

    return await describe_image(prepared.b64_jpeg)


def _crop_region(image: Image.Image, region: "SampleRegion") -> Image.Image:
    box = _region_box(image, region)
    if box is None:
        return image
    return image.crop(box)


def _region_box(image: Image.Image, region: "SampleRegion") -> tuple[int, int, int, int] | None:
    x = float(getattr(region, "x", 0.0) or 0.0)
    y = float(getattr(region, "y", 0.0) or 0.0)
    width = float(getattr(region, "width", 0.0) or 0.0)
    height = float(getattr(region, "height", 0.0) or 0.0)
    if width <= 0 or height <= 0:
        return None

    coordinate_space = str(getattr(region, "coordinate_space", "") or "normalized").lower()
    if coordinate_space in {"normalized", "screen_normalized", "image_normalized"}:
        x *= image.width
        width *= image.width
        y *= image.height
        height *= image.height

    left = max(0, min(image.width - 1, int(round(x))))
    top = max(0, min(image.height - 1, int(round(y))))
    right = max(left + 1, min(image.width, int(round(x + width))))
    bottom = max(top + 1, min(image.height, int(round(y + height))))
    if right <= left or bottom <= top:
        return None
    return (left, top, right, bottom)


__all__ = [
    "PersistedEvidenceCrop",
    "PreparedEvidenceImage",
    "describe_evidence_sample",
    "persist_evidence_crop",
    "prepare_evidence_image",
]
