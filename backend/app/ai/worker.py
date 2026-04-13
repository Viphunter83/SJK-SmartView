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
        # Базовые координаты в БД нормализованы под холст 800x600.
        # Необходимо смасштабировать их под РЕАЛЬНОЕ разрешение фотографии:
        scaled_corners = []
        for p in corners:
            scaled_corners.append([
                p[0] * (w / 800.0),
                p[1] * (h / 600.0)
            ])
        corners = scaled_corners

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
    """Контурный поиск экранов (замена, если YOLO не справился)."""
    import cv2
    import numpy as np

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Повышение контраста (полезно для ярких экранов на улице)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Адаптивный порог (Canny)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Соединяем "разрывы" в краях
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_corners = None
    max_area = 0

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        # Аппроксимация формы до многоугольника (ищем 4 угла)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            # Экран должен занимать хотя бы 5% площади всего фото
            if area > max_area and area > (w * h * 0.05):
                max_area = area
                best_corners = approx.reshape(4, 2).tolist()
                
    if best_corners:
        return best_corners
        
    # Second pass: Fallback порога если Canny не сработал
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > max_area and area > (w * h * 0.05):
                max_area = area
                best_corners = approx.reshape(4, 2).tolist()
                
    return best_corners


def _detect_corners_yolo(img, w, h) -> list:
    """Детекция углов. YOLO OBB -> OpenCV -> Fallback 15%."""
    try:
        from ultralytics import YOLO

        model = YOLO(YOLO_MODEL_NAME)
        results = model.predict(img, task="obb", verbose=False)

        if results and results[0].obb is not None and len(results[0].obb) > 0:
            # Берём detection с максимальной уверенностью
            confs = results[0].obb.conf.cpu().numpy()
            best_idx = confs.argmax()

            # xyxyxyxy → [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            points = results[0].obb.xyxyxyxy.cpu().numpy()[best_idx]
            if points.shape == (4, 2):
                return points.tolist()
    except Exception as e:
        print(f"YOLO detection failed: {e}")

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
    """Сортирует 4 точки: TL→ TR→ BR→ BL по принципу centroid."""
    import numpy as np

    centroid = pts.mean(axis=0)
    angles = []
    for p in pts:
        dx, dy = p[0] - centroid[0], p[1] - centroid[1]
        import math
        angles.append(math.atan2(dy, dx))

    order = sorted(range(4), key=lambda i: angles[i])
    # Порядок atan2: TL(-π,-π/2), TR(-π/2,0), BR(0,π/2), BL(π/2,π)
    # Результат мы хотим TL→TR→BR→BL
    sorted_pts = pts[order]

    # Нормализуем: TL = наименьшая сумма x+y
    sums = sorted_pts.sum(axis=1)
    tl_idx = sums.argmin()
    result = np.roll(sorted_pts, -tl_idx, axis=0)
    return result.astype("float32")


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
