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
    Премиум-генерация через Gemini 3 Pro Image.
    """
    # 1. Готовим "черновик" через OpenCV
    bg = _decode_image(background_bytes)
    cr = _decode_image(creative_bytes)
    h, w = bg.shape[:2]
    
    if not corners:
        corners = _detect_corners_opencv(bg, w, h)
    else:
        corners = _scale_corners(corners, w, h)
        
    corners_sorted = _sort_corners(np.array(corners, dtype="float32"))
    src_pts = np.array([[0, 0], [cr.shape[1], 0], [cr.shape[1], cr.shape[0]], [0, cr.shape[0]]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, corners_sorted)
    warped = cv2.warpPerspective(cr, M, (w, h))
    
    # Базовое наложение
    draft = _blend_images_advanced(bg, warped, corners_sorted)

    # 2. Магия Gemini для гармонизации
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY missing - returning standard blend")
        return cv2.imencode(".jpg", draft, [int(cv2.IMWRITE_JPEG_QUALITY), 95])[1].tobytes()

    try:
        client = genai.Client(api_key=api_key)
        
        # 3. Payload optimization (Downscaling for API stability)
        # Gemini handles large images, but two 4K+ images can exceed limits or timeout
        bg_optimized = _resize_image_for_api(background_bytes)
        cr_optimized = _resize_image_for_api(creative_bytes)

        # SCHEMA-driven Professional Prompt
        # Triggers: Thinking Mode, Geometric Consistency, Lighting Harmonization
        prompt = (
            "Style: Ultra-realistic high-end commercial advertising photography.\n"
            "Reference:\n"
            "  Image 1 (Background): Original environmental photograph.\n"
            "  Image 2 (Asset): Digital advertisement creative to be placed.\n"
            "Composition: Automatically identify the primary screen or advertisement surface in Image 1. "
            "Warp and map Image 2 onto this surface with mathematical precision.\n"
            "Thinking:\n"
            "  Enable: Multi-stage refinement.\n"
            "  Objective: Achieve 100% geometric consistency with the identified surface's perspective, "
            "curvature, and lens distortion.\n"
            "  Task: Apply professional Lighting Harmonization. Ensure the asset reflects ambient environment glow, "
            "mimics screen texture/pixel grain, and casts realistic micro-shadows on the bezels.\n"
            "Technical: Preserve original image noise grain; Output resolution 4K equivalents."
        )

        logger.info(f"Calling {GEMINI_MODEL_ID} with SCHEMA-native triggers...")
        
        # Send Multi-image request: [BG, Creative, Prompt]
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=[
                types.Part.from_bytes(data=bg_optimized, mime_type='image/jpeg'), # Image 1: BG
                types.Part.from_bytes(data=cr_optimized, mime_type='image/jpeg'), # Image 2: Asset
                prompt
            ]
        )

        # 4. Robust Safety & Response Handling
        # Check if model returned a valid candidate with content
        if not response.candidates or len(response.candidates) == 0:
            logger.warning("Gemini AI blocked the request (Safety Filters). Falling back to draft.")
            return _get_draft_bytes(draft)

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            logger.warning(f"Gemini AI returned empty content/blocked. Reason: {candidate.finish_reason}")
            return _get_draft_bytes(draft)

        # Extract image from response parts
        for part in candidate.content.parts:
            if part.inline_data:
                logger.info("Premium SCHEMA harmonization successful. Native AI-integrated image received.")
                return part.inline_data.data
        
        # Fallback to hybrid approach if native failing or not returning image
        logger.warning("SCHEMA native did not return image. Falling back to draft.")
        return _get_draft_bytes(draft)

    except Exception as e:
        logger.error(f"Gemini SCHEMA Critical Error: {e}. Falling back to OpenCV draft.")
        return _get_draft_bytes(draft)

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
