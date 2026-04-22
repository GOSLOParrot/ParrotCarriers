"""Brain vision helpers: VLM matching.

Implements lightweight VLM logic (compare against reference images)
and detail descriptions (describe_image) via Gemini API.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

from google import genai
from google.genai import types

from parrot.shared.snapshot import SnapshotEnvelope

logger = logging.getLogger(__name__)


async def compare_current_frame(
    current_b64: str,
    candidates: list[dict[str, Any]],
    model_name: str = "gemini-2.5-flash",
) -> tuple[str, float] | None:
    """Compare a current frame against multiple candidate reference images.

    Args:
        current_b64: Base64 JPEG data of the current frame.
        candidates: List of dicts, each with:
            "uuid": str
            "reference_image_b64": str (Base64 JPEG data)
            "label": str
        model_name: The Gemini model to use.

    Returns:
        A tuple of (matched_uuid, confidence_score [0.0-1.0]), or None if no match.
    """
    if not candidates:
        return None

    try:
        from parrot.shared.config import config
        client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e:
        logger.warning("Failed to initialize GenAI client: %s", e)
        return None

    # Prepare prompt parts:
    # 1. The current frame
    # 2. For each candidate, their reference image and UUID/label
    # 3. The prompt asking to find the best match
    
    parts = []
    
    # Target frame
    target_data = base64.b64decode(current_b64)
    parts.append(types.Part.from_bytes(data=target_data, mime_type="image/jpeg"))
    parts.append("This is the current view.")
    
    # Candidates
    for i, c in enumerate(candidates, 1):
        if not c.get("reference_image_b64"):
            continue
            
        c_data = base64.b64decode(c["reference_image_b64"])
        parts.append(types.Part.from_bytes(data=c_data, mime_type="image/jpeg"))
        parts.append(f"Candidate {i}: UUID={c['uuid']}, Label='{c['label']}'.")
        
    parts.append(
        "Does the current view show exactly the same physical object as any of the candidates? "
        "It must be the specific instance, not just the same category. "
        "If yes, return JSON with 'match_uuid' and 'confidence' (0.0 to 1.0). "
        "If no, return JSON with 'match_uuid': null and 'confidence': 0.0."
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=parts,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        
        import json
        result = json.loads(response.text)
        
        match_uuid = result.get("match_uuid")
        confidence = float(result.get("confidence", 0.0))
        
        if match_uuid and confidence > 0.5:
            return match_uuid, confidence
            
        return None
        
    except Exception as e:
        logger.exception("VLM compare failed: %s", e)
        return None


async def describe_image(
    b64_data: str,
    model_name: str = "gemini-2.5-flash",
) -> str:
    """Describe the fine details of an image.

    Used by the L2 confirm_new flow to generate detailed object descriptions.
    """
    try:
        from parrot.shared.config import config
        client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e:
        logger.warning("Failed to initialize GenAI client: %s", e)
        return "A newly discovered object (image description failed)."

    try:
        image_data = base64.b64decode(b64_data)
        part = types.Part.from_bytes(data=image_data, mime_type="image/jpeg")

        prompt = (
            "Describe the central object in this image in detail. "
            "Focus on its visual characteristics: color, material, shape, brand (if visible), "
            "model, state, and any unique distinguishing marks. "
            "Keep the description factual and concise."
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[part, prompt],
        )
        
        return response.text or "A newly discovered object."
        
    except Exception as e:
        logger.exception("VLM describe failed: %s", e)
        return "A newly discovered object (image description failed)."
