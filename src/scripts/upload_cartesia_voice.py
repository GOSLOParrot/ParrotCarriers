"""Upload voice samples to Cartesia Voice Design API and return a reusable voice_id.

Usage:
    python src/scripts/upload_cartesia_voice.py \
        --samples FilePort3/Ner_LineB_voice_config_pack_20260511/voice_samples/ner_sample_002.wav \
                  FilePort3/Ner_LineB_voice_config_pack_20260511/voice_samples/ner_sample_003.wav \
                  FilePort3/Ner_LineB_voice_config_pack_20260511/voice_samples/ner_sample_004.wav \
        --name "ner_test_v1" \
        --language "ja"

    # or auto-discover all WAV files in a directory:
    python src/scripts/upload_cartesia_voice.py \
        --samples-dir FilePort3/Ner_LineB_voice_config_pack_20260511/voice_samples \
        --name "ner_test_v1"

After success, add the printed VOICE_ID to your ECS .env:
    PARROT_LINEB_CARTESIA_VOICE_ID=<voice_id>
    PARROT_LINEB_TTS_PROVIDER=cartesia

Cartesia docs: https://docs.cartesia.ai/build-with-cartesia/voice-lab/voice-cloning
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _require_cartesia() -> "Any":
    try:
        import cartesia  # type: ignore[import]
        return cartesia
    except ImportError:
        print(
            "ERROR: cartesia package not installed.\n"
            "Install with: pip install cartesia\n"
            "(This is the Cartesia Python SDK, separate from livekit-agents.)"
        )
        sys.exit(1)


def upload_voice(
    sample_paths: list[Path],
    name: str,
    language: str,
    api_key: str,
) -> dict:
    import httpx

    print(f"\nUploading {len(sample_paths)} samples as voice '{name}' (language={language})...")

    # Cartesia Instant Voice Cloning endpoint
    # POST https://api.cartesia.ai/voices/clone/clip
    # Docs: https://docs.cartesia.ai/api-reference/voices/clone-voice-from-clip
    url = "https://api.cartesia.ai/voices/clone/clip"
    headers = {
        "X-API-Key": api_key,
        "Cartesia-Version": "2024-06-10",
    }

    files = []
    opened = []
    try:
        for path in sample_paths:
            f = open(path, "rb")  # noqa: WPS515 - kept open until request completes
            opened.append(f)
            files.append(("clip", (path.name, f, "audio/wav")))

        data = {
            "name": name,
            "language": language,
            "mode": "similarity",  # keep timbre/style without hard voice lock
            "enhance": "true",     # Cartesia's noise reduction pass
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(url, headers=headers, data=data, files=files)

        if response.status_code not in (200, 201):
            print(f"ERROR: Cartesia API returned {response.status_code}")
            print(response.text)
            sys.exit(1)

        return response.json()
    finally:
        for f in opened:
            f.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload samples to Cartesia Voice Design.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--samples", nargs="+", type=Path, help="WAV file paths to upload")
    group.add_argument("--samples-dir", type=Path, help="Directory of WAV files to upload")
    parser.add_argument("--name", default="ner_test_v1", help="Voice name in Cartesia")
    parser.add_argument("--language", default="ja", help="Primary language hint (e.g. ja, zh, en)")
    parser.add_argument("--max-clips", type=int, default=5, help="Max clips to upload (default 5)")
    args = parser.parse_args()

    api_key = os.getenv("CARTESIA_API_KEY", "").strip()
    if not api_key:
        print("ERROR: CARTESIA_API_KEY not set.\n"
              "Get one from https://cartesia.ai/dashboard and set:\n"
              "  $env:CARTESIA_API_KEY='sk-...'")
        sys.exit(1)

    if args.samples_dir:
        all_wavs = sorted(args.samples_dir.glob("*.wav"))
        # exclude the enhanced full audio
        sample_paths = [p for p in all_wavs if not p.name.startswith("_")]
    else:
        sample_paths = args.samples

    # Filter to existing files only
    sample_paths = [p for p in sample_paths if p.is_file()]
    if not sample_paths:
        print("ERROR: No WAV files found.")
        sys.exit(1)

    # Trim to max_clips; prefer longer files (better quality reference)
    if len(sample_paths) > args.max_clips:
        sample_paths = sorted(sample_paths, key=lambda p: p.stat().st_size, reverse=True)
        sample_paths = sample_paths[:args.max_clips]
        print(f"Using top {args.max_clips} largest files for upload.")

    print("Selected clips:")
    for p in sample_paths:
        size_kb = p.stat().st_size // 1024
        print(f"  {p.name}  ({size_kb} KB)")

    try:
        import httpx  # noqa: F401 - availability check
    except ImportError:
        print("ERROR: httpx not installed. Run: pip install httpx")
        sys.exit(1)

    result = upload_voice(sample_paths, args.name, args.language, api_key)

    voice_id = result.get("id") or result.get("voice_id") or ""
    print("\n" + "=" * 50)
    print("Cartesia Voice Design upload complete.")
    print(f"  Voice name : {result.get('name', args.name)}")
    print(f"  Voice ID   : {voice_id}")
    print("=" * 50)

    if voice_id:
        print("\nAdd to ECS .env:")
        print(f"  CARTESIA_API_KEY={api_key[:8]}...  (already set)")
        print(f"  PARROT_LINEB_CARTESIA_VOICE_ID={voice_id}")
        print(f"  PARROT_LINEB_TTS_PROVIDER=cartesia")

        # Save to local report (gitignored directory)
        report_dir = Path("FilePort3") / "Ner_LineB_voice_config_pack_20260511" / "voice_samples"
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "cartesia_voice_id": voice_id,
            "voice_name": result.get("name", args.name),
            "language": args.language,
            "uploaded_clips": [str(p) for p in sample_paths],
            "raw_response": result,
        }
        report_path = report_dir / "cartesia_voice_result.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nResult saved: {report_path}")
    else:
        print("\nWARNING: Could not extract voice_id from response.")
        print("Full response:", json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
