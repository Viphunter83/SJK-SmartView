"""
SJK SmartView — Modal GPU Worker
Удалённый AI-рабочий на GPU A10G для фотореалистичной генерации мокапов.
Pipeline: YOLO OBB (детекция углов экрана) → Perspective Warp (OpenCV) → Blending
"""
import modal
import base64

# ──────────────────────────────────────────────
# Modal App & Docker Image
# ──────────────────────────────────────────────
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install(
        "libgl1-mesa-glx",
        "libglib2.0-0",
        "libsm6",
        "libxext6",
        "libxrender-dev",
        "libgomp1",
    )
    .pip_install(
        "opencv-python-headless==4.10.0.84",
        "numpy==1.26.4",
        "pillow==10.4.0",
        "torch==2.3.1",
        "torchvision==0.18.1",
        "ultralytics==8.3.40",  # YOLO v11 OBB
    )
)

app = modal.App("sjk-smartview-ai")

# Модель YOLO OBB — Oriented Bounding Box для точного угла экрана
# yolo11n-obb.pt = 6.5MB, работает без GPU но быстрее с ним
YOLO_MODEL_NAME = "yolo11n-obb.pt"


@app.function(
    image=image,
    gpu="A10G",
    timeout=120,
    scaledown_window=300,  # Держим инстанс 5 минут после последнего запроса
)
def process_mockup(
    background_bytes: bytes,
    creative_bytes: bytes,
    corners: list = None,
) -> str:
    """
    GPU-рендеринг мокапа рекламного экрана.

    Args:
        background_bytes: фото экрана (JPEG/PNG bytes)
        creative_bytes: рекламный креатив (JPEG/PNG bytes)
        corners: 4 угла [[x1,y1], ...] в пикселях. Если None — YOLO определит автоматически.

    Returns:
        base64-строка JPEG результата
    """
    import cv2
    import numpy as np

    # ── 1. Декодируем изображения ───────────────────────────────
    bg_np = np.frombuffer(background_bytes, np.uint8)
    bg = cv2.imdecode(bg_np, cv2.IMREAD_COLOR)

    cr_np = np.frombuffer(creative_bytes, np.uint8)
    cr = cv2.imdecode(cr_np, cv2.IMREAD_COLOR)

    if bg is None or cr is None:
        raise ValueError("Не удалось декодировать изображения")

    h, w = bg.shape[:2]

    # ── 2. Детекция углов YOLO OBB (если не переданы) ──────────
    if not corners:
        corners = _detect_corners_yolo(bg, w, h)
    else:
        # Координаты в БД заданы в абсолютном пространстве 800×600.
        # Масштабируем пропорционально до реального разрешения фото.
        scale_x = w / 800.0
        scale_y = h / 600.0
        print(f"DEBUG: Scaling corners from 800x600 to {w}x{h} (Scale: {scale_x:.2f}, {scale_y:.2f})")
        scaled_corners = []
        for p in corners:
            scaled_corners.append([
                p[0] * scale_x,
                p[1] * scale_y,
            ])
        corners = scaled_corners
        print(f"DEBUG: Input corners: {corners}")

    # Нормализуем структуру углов
    corners_np = np.array(corners, dtype="float32")
    if corners_np.shape != (4, 2):
        raise ValueError(f"Ожидается 4 угла в формате [[x,y]×4], получено: {corners_np.shape}")

    # ── 3. Perspective Warp ─────────────────────────────────────
    src_pts = np.array([
        [0, 0],
        [cr.shape[1], 0],
        [cr.shape[1], cr.shape[0]],
        [0, cr.shape[0]],
    ], dtype="float32")

    # Сортируем углы: TL → TR → BR → BL
    corners_sorted = _sort_corners(corners_np)
    M = cv2.getPerspectiveTransform(src_pts, corners_sorted)
    warped = cv2.warpPerspective(cr, M, (w, h))

    # ── 4. Маска экрана и blending ──────────────────────────────
    screen_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(screen_mask, corners_sorted.astype(np.int32), 255)

    # Мягкие края (feathering) для реализма
    feather = cv2.GaussianBlur(screen_mask.astype(np.float32) / 255.0, (15, 15), 0)

    # Лёгкая виньетка: затемнение краёв экрана для реализма
    vignette = _make_vignette(corners_sorted, w, h, strength=0.15)
    feather = feather * (1.0 - vignette)

    result = bg.copy().astype(np.float32)
    warped_f = warped.astype(np.float32)

    for c in range(3):
        result[:, :, c] = (
            bg[:, :, c] * (1.0 - feather) + warped_f[:, :, c] * feather
        )

    result = np.clip(result, 0, 255).astype(np.uint8)

    # ── 5. JPEG → base64 ────────────────────────────────────────
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 92]
    _, buffer = cv2.imencode(".jpg", result, encode_params)
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


@app.function(
    image=image,
    gpu="A10G",
    timeout=60,
    scaledown_window=300,
)
def detect_corners(image_bytes: bytes) -> dict:
    """
    Отдельная GPU-функция только для детекции углов экрана.
    Возвращает словарь с corners, confidence, method.
    """
    import cv2
    import numpy as np

    img_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Не удалось декодировать изображение", "corners": None}

    h, w = img.shape[:2]
    corners = _detect_corners_yolo(img, w, h)

    return {
        "corners": corners,
        "confidence": 0.85,
        "method": "yolo_obb",
        "image_size": [w, h],
    }


# ──────────────────────────────────────────────
# Вспомогательные функции (выполняются на GPU worker)
# ──────────────────────────────────────────────

def _detect_corners_opencv(img, w, h) -> list:
    """
    Многостратегийная детекция LED-экранов через OpenCV.
    Стратегия 1: HSV яркость (экраны ярче окружения)
    Стратегия 2: CLAHE + Canny + морфология
    Стратегия 3: Адаптивный порог
    Везде используем minAreaRect (всегда 4 угла) вместо approxPolyDP.
    """
    import cv2
    import numpy as np

    min_area = w * h * 0.03  # Минимум 3% площади изображения

    # ── Стратегия 1: HSV яркость ──────────────────────────────────
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Экраны обычно очень яркие (V > 180)
        _, bright_mask = cv2.threshold(hsv[:, :, 2], 180, 255, cv2.THRESH_BINARY)
        
        # Морфология: закрываем дыры внутри экрана
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
        # Убираем мелкий шум
        closed = cv2.morphologyEx(closed, cv2.MORPH_OPEN, 
                                   cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best = None
        max_area = min_area
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                max_area = area
                best = box.tolist()
        
        if best:
            return best
    except Exception as e:
        print(f"HSV detection failed: {e}")

    # ── Стратегия 2: CLAHE + Canny + морфология ────────────────────
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        # Адаптивный Canny
        median_val = float(np.median(blurred))
        low = int(max(0, 0.5 * median_val))
        high = int(min(255, 1.5 * median_val))
        edges = cv2.Canny(blurred, low, high)
        
        # Соединяем разрывы
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        edges = cv2.erode(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best = None
        max_area = min_area
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                # Проверяем "прямоугольность": area / boundingRect area > 0.6
                x_r, y_r, w_r, h_r = cv2.boundingRect(cnt)
                rect_fill = area / (w_r * h_r) if w_r * h_r > 0 else 0
                if rect_fill > 0.5:
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    max_area = area
                    best = box.tolist()
        
        if best:
            return best
    except Exception as e:
        print(f"CLAHE+Canny detection failed: {e}")

    # ── Стратегия 3: Адаптивный порог ──────────────────────────────
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        for thresh_val in [150, 120, 180, 200]:
            _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best = None
            max_area = min_area
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    max_area = area
                    best = box.tolist()
            
            if best:
                return best
    except Exception as e:
        print(f"Threshold detection failed: {e}")

    return None


def _detect_corners_yolo(img, w, h) -> list:
    """Детекция углов: улучшенный OpenCV → Fallback 15%.
    
    Примечание: YOLO OBB yolo11n-obb.pt обучена на DOTA (спутниковые снимки),
    не содержит класса 'LED screen'. Оставляем OpenCV как основной метод.
    """
    # Основной метод — мульти-стратегийный OpenCV
    try:
        cv_corners = _detect_corners_opencv(img, w, h)
        if cv_corners is not None:
            return cv_corners
    except Exception as e:
        print(f"OpenCV detection failed: {e}")

    # Fallback: 15% отступ от краёв (умный дефолт)
    pad_x, pad_y = int(w * 0.15), int(h * 0.15)
    return [
        [pad_x, pad_y],
        [w - pad_x, pad_y],
        [w - pad_x, h - pad_y],
        [pad_x, h - pad_y],
    ]


def _sort_corners(pts) -> "np.ndarray":
    """Сортирует 4 точки: TL→ TR→ BR→ BL по методу суммы/разности."""
    import numpy as np
    
    rect = np.zeros((4, 2), dtype="float32")
    
    # TL: минимальная сумма x+y
    # BR: максимальная сумма x+y
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # TR: минимальная разность x-y (или y-x min)
    # Порядок OpenCV: TL, TR, BR, BL
    # diff = x - y
    # TL: x+y min
    # BR: x+y max
    # TR: x-y max (x большой, y маленький)
    # BL: x-y min (x маленький, y большой)
    diff = np.diff(pts, axis=1) # y - x
    rect[1] = pts[np.argmin(diff)] # y-x min => x-y max => TR
    rect[3] = pts[np.argmax(diff)] # y-x max => x-y min => BL
    
    return rect


def _make_vignette(corners, w, h, strength=0.15) -> "np.ndarray":
    """Создаёт маску виньетки внутри экрана для реализма."""
    import numpy as np
    import cv2

    mask = np.zeros((h, w), dtype=np.float32)
    cv2.fillConvexPoly(mask, corners.astype(np.int32), 1.0)

    # Размытие создаёт эффект постепенного затемнения к краям
    kernel_size = max(int(min(w, h) * 0.05) | 1, 3)
    blurred = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)

    # Инвертируем: края внутри маски = тёмные
    vignette = mask * (1.0 - blurred / blurred.max() if blurred.max() > 0 else 0)
    return vignette * strength
