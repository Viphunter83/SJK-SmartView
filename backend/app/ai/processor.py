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
        
        # 1. Robust Image Parsing & Normalization (Convert to strictly JPEG to prevent 500 Internal Server Error)
        # Google GenAI backend strictly expects standard jpeg/png. Alpha channels (RGBA) often cause 500 errors.
        bg_pil = Image.open(io.BytesIO(background_bytes)).convert("RGB")
        # Reduced max_dim to 1536 to prevent backend Out-Of-Memory 500 Errors
        bg_pil.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        bg_bytes_io = io.BytesIO()
        bg_pil.save(bg_bytes_io, format="JPEG", quality=85)
        bg_part = types.Part.from_bytes(data=bg_bytes_io.getvalue(), mime_type="image/jpeg")

        cr_pil = Image.open(io.BytesIO(creative_bytes)).convert("RGB")
        cr_pil.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        cr_bytes_io = io.BytesIO()
        cr_pil.save(cr_bytes_io, format="JPEG", quality=85)
        cr_part = types.Part.from_bytes(data=cr_bytes_io.getvalue(), mime_type="image/jpeg")

        # 2. SCHEMA v4.3 Prompt Engineering (Narrative Approach)
        # Optimized for Nano Banana Pro's advanced spatial reasoning.
        
        spatial_context = ""
        if corners:
            spatial_context = (
                f"The target display surface is precisely located at these coordinates: {corners}. "
                "Use this as the foundation for your pixel-perfect mapping."
            )

        prompt = (
            "A high-end professional commercial photograph for an advertising campaign. "
            "Identify the main digital screen or billboard billboard in Image 1 and integrate the creative asset from Image 2 onto it. "
            f"{spatial_context} "
            "The integration must be seamless, with reflections, shadows, and ambient lighting matching the environment perfectly. "
            "Maintain occlusion integrity: people, vehicles, or structures in the foreground must remain in front of the screen. "
            "Output the final result in 2K high-definition resolution."
        )

        logger.info("Calling Nano Banana Pro (Gemini 3 Pro Image Preview) [2K Mode]...")
        
        # 3. Native SDK Call (Nano Banana 2026 Syntax)
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, bg_part, cr_part],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9"
                )
            )
        )

        # 4. Response Extraction & Validation
        if getattr(response, "candidates", None) is None:
            logger.error("Nano Banana: Empty candidates. Safety block suspected.")
            raise ValueError("EMPTY_CANDIDATES")

        for part in response.parts:
            # Safest method: grab raw bytes coming from the API directly
            if getattr(part, 'inline_data', None):
                logger.info("Nano Banana 2 (Flash): Image generated & extracted successfully from inline_data.")
                return part.inline_data.data
            
            # Fallback if google-genai returns a wrapper object instead of inline_data
            if hasattr(part, 'as_image') or hasattr(part, 'image'):
                logger.info("Nano Banana 2 (Flash): Extracted image object, converting to bytes.")
                img = part.as_image() if hasattr(part, 'as_image') else part.image
                img_byte_arr = io.BytesIO()
                
                try:
                    # Attempt standard PIL method
                    img.save(img_byte_arr, format='JPEG', quality=95)
                except Exception:
                    try:
                        # Fallback for wrapper classes that don't accept 'format'
                        img.save(img_byte_arr)
                    except Exception as fallback_e:
                        logger.error(f"Failed to serialize Image object: {fallback_e}")
                        raise ValueError("UNSUPPORTED_IMAGE_OBJECT")
                
                return img_byte_arr.getvalue()
        
        raise ValueError("NO_IMAGE_RETURNED")

    except Exception as e:
        import traceback
        logger.error("NANO BANANA CRITICAL ERROR [%s]: %s", type(e).__name__, str(e))
        logger.error(traceback.format_exc())
        # Safety fallback to OpenCV standard processing
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
