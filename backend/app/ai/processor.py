"""
SJK SmartView — AI Image Processor (Local)
Handles OpenCV image processing and Gemini 3 Pro Image integration.
"""
import os
import cv2
import numpy as np
import base64
import logging
from PIL import Image
import io
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Фиксированная модель для премиум-генерации (Gemini 3 Pro Image)
# Используем gemini-3-pro-image-preview (Nano Banana Pro) для лучшего качества гармонизации
GEMINI_MODEL_ID = "gemini-3-pro-image-preview"

def process_mockup_standard(
    background_bytes: bytes,
    creative_bytes: bytes,
    corners: list = None,
) -> bytes:
    """
    Стандартная генерация (OpenCV Perspective Warp + Blending).
    """
    bg = _decode_image(background_bytes)
    cr = _decode_image(creative_bytes)
    h, w = bg.shape[:2]

    # Детекция или масштабирование углов
    if not corners:
        corners = _detect_corners_opencv(bg, w, h)
    else:
        corners = _scale_corners(corners, w, h)

    corners_sorted = _sort_corners(np.array(corners, dtype="float32"))
    
    # Perspective Warp
    src_pts = np.array([[0, 0], [cr.shape[1], 0], [cr.shape[1], cr.shape[0]], [0, cr.shape[0]]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, corners_sorted)
    warped = cv2.warpPerspective(cr, M, (w, h))

    # Качественный бленд
    result = _blend_images_advanced(bg, warped, corners_sorted)
    
    _, buffer = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return buffer.tobytes()

async def process_mockup_premium(
    background_bytes: bytes,
    creative_bytes: bytes,
    corners: list = None,
) -> bytes:
    """
    Premium generation via Gemini 3 Pro Image (SCHEMA v4.0).
    Uses Native AI mapping with 'Flexible Anchors' and 'Thinking: HIGH'.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY missing - returning standard blend")
        # For security fallback, we still need a draft if API key is missing
        return process_mockup_standard(background_bytes, creative_bytes, corners)

    try:
        client = genai.Client(api_key=api_key)
        
        # 1. Payload Optimization (Balance between quality and API limits)
        bg_optimized = _resize_image_for_api(background_bytes, max_dim=3072)
        cr_optimized = _resize_image_for_api(creative_bytes, max_dim=2048)

        # 2. SCHEMA v4.0 Prompt Engineering (Systemic Approach)
        # We explicitly label the images and provide spatial triggers.
        
        spatial_hint = ""
        if corners:
            spatial_hint = (
                f"\nSpatial Hint: The target display surface is approximately located at these coordinates: {corners}. "
                "Use these as anchor points, but verify and refine the exact pixel-perfect edges and stereometry yourself."
            )

        prompt = (
            "[SCHEMA v4.0: High-Fidelity DOOH Integration]\n"
            "CONTEXT: Professional advertising mockup for Shojiki Group Vietnam.\n"
            "TASK: Integrat Image 2 (Asset) into the high-priority display surface found in Image 1 (Environment).\n"
            f"{spatial_hint}\n"
            "COGNITIVE STEPS:\n"
            "1. Scene Analysis: Identify the primary digital screen, billboard, or LED surface.\n"
            "2. Geometric Mapping: Warp Image 2 to fit the surface perfectly, respecting perspective and lens distortion.\n"
            "3. Photorealistic Blending: Inherit ambient lighting, reflection, and grain from Image 1.\n"
            "4. Occlusion Handling: If any foreground objects (tree, lamp, person) cover the screen, "
            "ensure Image 2 is mapped BEHIND them.\n"
            "OUTPUT: Return ONLY the final integrated image in high resolution."
        )

        logger.info(f"Calling {GEMINI_MODEL_ID} with Thinking: HIGH and SCHEMA v4.0...")
        
        # 3. Native SDK Call with Thinking Budget
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=[
                types.Part.from_bytes(data=bg_optimized, mime_type='image/jpeg'),
                types.Part.from_bytes(data=cr_optimized, mime_type='image/jpeg'),
                prompt
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.HIGH
                ),
                response_modalities=['IMAGE']
            )
        )

        # 4. Critical Response Handling
        if not response.candidates or len(response.candidates) == 0:
            logger.error("Gemini AI blocked the request (No candidates). Check Safety Filters.")
            raise ValueError("AI_SAFETY_BLOCK: The request was blocked by safety filters.")

        candidate = response.candidates[0]
        if candidate.finish_reason != types.FinishReason.STOP and candidate.finish_reason != types.FinishReason.MAX_TOKENS:
            logger.error(f"Gemini integration failed. Finish Reason: {candidate.finish_reason}")
            raise ValueError(f"AI_PIPELINE_ERROR: {candidate.finish_reason}")

        for part in candidate.content.parts:
            if part.inline_data:
                logger.info("SCHEMA v4.0 Premium harmonization successful.")
                return part.inline_data.data
        
        raise ValueError("AI_PART_ERROR: Model did not return image data.")

    except Exception as e:
        logger.error(f"Gemini SCHEMA v4.0 Critical Error: {e}")
        # Only fallback if it's a connectivity/API error, not a logic error.
        # But for user experience, returning standard blend as last resort.
        return process_mockup_standard(background_bytes, creative_bytes, corners)

def _get_draft_bytes(draft):
    """Encodes OpenCV draft to bytes for fallback."""
    _, draft_buffer = cv2.imencode(".jpg", draft, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return draft_buffer.tobytes()

def _resize_image_for_api(img_bytes: bytes, max_dim: int = 2048) -> bytes:
    """Resizes image to max_dim if necessary for API payload stability."""
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return img_bytes
        
    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return img_bytes
        
    scale = max_dim / float(max(h, w))
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    _, buffer = cv2.imencode(".jpg", resized, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return buffer.tobytes()

def detect_corners_local(image_bytes: bytes) -> dict:
    """Локальная детекция углов через OpenCV."""
    img = _decode_image(image_bytes)
    h, w = img.shape[:2]
    corners = _detect_corners_opencv(img, w, h)
    return {"corners": corners, "image_size": [w, h]}

# ─────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────

def _decode_image(img_bytes: bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def _scale_corners(corners, w, h):
    scale_x, scale_y = w / 800.0, h / 600.0
    return [[p[0] * scale_x, p[1] * scale_y] for p in corners]

def _sort_corners(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # TL
    rect[2] = pts[np.argmax(s)] # BR
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # TR
    rect[3] = pts[np.argmax(diff)] # BL
    return rect

def _blend_images_advanced(bg, warped, corners_sorted):
    h, w = bg.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(mask, corners_sorted.astype(np.int32), 255)
    
    feather = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)
    
    # Виньетка
    vignette = np.zeros((h, w), dtype=np.float32)
    cv2.fillConvexPoly(vignette, corners_sorted.astype(np.int32), 1.0)
    v_blurred = cv2.GaussianBlur(vignette, (41, 41), 0)
    v_mask = vignette * (1.0 - v_blurred / (v_blurred.max() + 1e-6))
    feather = feather * (1.0 - v_mask * 0.15)

    result = bg.astype(np.float32)
    warped_f = warped.astype(np.float32)
    for i in range(3):
        result[:,:,i] = bg[:,:,i] * (1.0 - feather) + warped_f[:,:,i] * feather
    
    return np.clip(result, 0, 255).astype(np.uint8)

def _detect_corners_opencv(img, w, h):
    # Упрощенная логика из worker (OpenCV Multi-strategy)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        best_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(best_cnt) > (w * h * 0.02):
            rect = cv2.minAreaRect(best_cnt)
            return cv2.boxPoints(rect).tolist()
            
    # Fallback
    pad_x, pad_y = int(w * 0.15), int(h * 0.15)
    return [[pad_x, pad_y], [w - pad_x, pad_y], [w - pad_x, h - pad_y], [pad_x, h - pad_y]]
