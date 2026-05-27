"""A10/CV dataset export helpers for accepted object samples.

Exports are derived artifacts. The object/sample catalog remains the source of
truth; this module copies accepted sample crops into COCO/YOLO-compatible
folders and writes a manifest that preserves Parrot UUID bindings.
"""

from __future__ import annotations

import json
import shutil
import time
import uuid as uuid_lib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from parrot.brain.vision.object_discovery import list_object_samples, vision_root

SCHEMA_VERSION = "a10_export_v1"


@dataclass(frozen=True)
class A10ExportRecord:
    sample_uuid: str
    object_uuid: str
    photo_uuid: str
    object_ref_id: str
    label: str
    category: str
    source_crop_path: str
    export_image_path: str
    export_label_path: str
    width: int
    height: int
    bbox: dict[str, Any] = field(default_factory=dict)
    quality_flags: list[str] = field(default_factory=list)
    review_status: str = ""

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def export_accepted_samples_for_a10(
    *,
    object_uuid: str = "",
    export_uuid: str = "",
    subset: str = "train",
    copy_images: bool = True,
) -> dict[str, Any]:
    """Export accepted ObjectSamples to COCO and YOLO directory layouts."""
    export_uuid = str(export_uuid or _new_prefixed_id("exp")).strip()
    subset = _safe_subset(subset)
    samples = [
        sample
        for sample in list_object_samples(object_uuid=object_uuid, accepted_only=True)
        if str(sample.get("object_uuid") or "")
    ]

    export_root = vision_root() / "exports" / "a10" / _safe_path_segment(export_uuid)
    coco_images_dir = export_root / "coco" / "images" / subset
    coco_annotations_dir = export_root / "coco" / "annotations"
    yolo_images_dir = export_root / "yolo" / "images" / subset
    yolo_labels_dir = export_root / "yolo" / "labels" / subset
    for path in (coco_images_dir, coco_annotations_dir, yolo_images_dir, yolo_labels_dir):
        path.mkdir(parents=True, exist_ok=True)

    categories = _category_map(samples)
    records: list[A10ExportRecord] = []
    coco_images: list[dict[str, Any]] = []
    coco_annotations: list[dict[str, Any]] = []

    for image_id, sample in enumerate(samples, start=1):
        crop_path = Path(str(sample.get("crop_path") or ""))
        if not crop_path.is_file():
            continue
        width, height = _image_size(crop_path)
        if width <= 0 or height <= 0:
            continue
        sample_uuid = str(sample.get("sample_uuid") or f"sample_{image_id}")
        category_name = _category_name(sample)
        category_id = categories[category_name]
        image_name = f"{_safe_path_segment(sample_uuid)}.jpg"
        coco_image_path = coco_images_dir / image_name
        yolo_image_path = yolo_images_dir / image_name
        if copy_images:
            shutil.copyfile(crop_path, coco_image_path)
            shutil.copyfile(crop_path, yolo_image_path)

        yolo_label_path = yolo_labels_dir / f"{Path(image_name).stem}.txt"
        yolo_label_path.write_text(f"{category_id - 1} 0.500000 0.500000 1.000000 1.000000\n", encoding="utf-8")
        coco_images.append(
            {
                "id": image_id,
                "file_name": f"images/{subset}/{image_name}",
                "width": width,
                "height": height,
                "parrot_sample_uuid": sample_uuid,
                "parrot_object_uuid": str(sample.get("object_uuid") or ""),
                "parrot_photo_uuid": str(sample.get("photo_uuid") or ""),
            }
        )
        coco_annotations.append(
            {
                "id": image_id,
                "image_id": image_id,
                "category_id": category_id,
                "bbox": [0, 0, width, height],
                "area": width * height,
                "iscrowd": 0,
                "attributes": {
                    "sample_uuid": sample_uuid,
                    "object_uuid": str(sample.get("object_uuid") or ""),
                    "photo_uuid": str(sample.get("photo_uuid") or ""),
                    "object_ref_id": str(sample.get("object_ref_id") or ""),
                    "source_bbox": dict(sample.get("bbox") or {}),
                    "quality_flags": list(sample.get("quality_flags") or []),
                    "review_status": str(sample.get("review_status") or ""),
                    "source": str(sample.get("created_by") or ""),
                },
            }
        )
        records.append(
            A10ExportRecord(
                sample_uuid=sample_uuid,
                object_uuid=str(sample.get("object_uuid") or ""),
                photo_uuid=str(sample.get("photo_uuid") or ""),
                object_ref_id=str(sample.get("object_ref_id") or ""),
                label=str(sample.get("label") or ""),
                category=category_name,
                source_crop_path=str(crop_path),
                export_image_path=str(yolo_image_path),
                export_label_path=str(yolo_label_path),
                width=width,
                height=height,
                bbox=dict(sample.get("bbox") or {}),
                quality_flags=list(sample.get("quality_flags") or []),
                review_status=str(sample.get("review_status") or ""),
            )
        )

    coco = {
        "info": {
            "description": "ParrotCarriers accepted object samples export",
            "version": SCHEMA_VERSION,
            "export_uuid": export_uuid,
            "created_at_ms": int(time.time() * 1000),
        },
        "images": coco_images,
        "annotations": coco_annotations,
        "categories": [
            {"id": category_id, "name": name, "supercategory": "object"}
            for name, category_id in sorted(categories.items(), key=lambda item: item[1])
        ],
    }
    coco_path = coco_annotations_dir / f"instances_{subset}.json"
    coco_path.write_text(json.dumps(coco, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")

    names = [name for name, _category_id in sorted(categories.items(), key=lambda item: item[1])]
    (export_root / "yolo" / "obj.names").write_text("\n".join(names) + ("\n" if names else ""), encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "export_uuid": export_uuid,
        "subset": subset,
        "export_root": str(export_root),
        "sample_count": len(records),
        "source_sample_count": len(samples),
        "object_uuid": object_uuid,
        "coco_annotations_path": str(coco_path),
        "yolo_names_path": str(export_root / "yolo" / "obj.names"),
        "records": [record.as_json() for record in records],
        "audit": {
            "source_of_truth": "vision_catalog_object_samples_jsonl",
            "accepted_samples_only": True,
            "identity_binding": "export_only_no_identity_mutation",
        },
    }
    manifest_path = export_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return {
        "action": "vision.a10_export.create",
        "success": True,
        "export_uuid": export_uuid,
        "export_root": str(export_root),
        "manifest_path": str(manifest_path),
        "sample_count": len(records),
        "coco_annotations_path": str(coco_path),
        "yolo_names_path": str(export_root / "yolo" / "obj.names"),
    }


def _category_map(samples: list[dict[str, Any]]) -> dict[str, int]:
    names = sorted({_category_name(sample) for sample in samples}) or ["object"]
    return {name: index for index, name in enumerate(names, start=1)}


def _category_name(sample: dict[str, Any]) -> str:
    return _safe_label(str(sample.get("category") or sample.get("label") or "object"))


def _safe_label(value: str) -> str:
    label = " ".join(str(value or "").strip().split())
    return label[:80] or "object"


def _image_size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            return image.size
    except Exception:
        return (0, 0)


def _safe_subset(value: str) -> str:
    normalized = _safe_path_segment(value)
    return normalized if normalized in {"train", "val", "test"} else "train"


def _safe_path_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in str(value or ""))[:160] or "item"


def _new_prefixed_id(prefix: str) -> str:
    factory = getattr(uuid_lib, "uuid7", None)
    value = factory() if callable(factory) else uuid_lib.uuid4()
    return f"{prefix}_{value.hex}"


__all__ = ["A10ExportRecord", "export_accepted_samples_for_a10"]
