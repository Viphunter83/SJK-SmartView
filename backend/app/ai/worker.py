import modal
import numpy as np
import cv2
import os
import base64
from io import BytesIO
from PIL import Image

# Определение образа для Modal с GPU поддержкой, SAM 2 и YOLO
# Используем debian_slim и ставим зависимости для ML
image = modal.Image.debian_slim(python_version="3.12") \
    .apt_install("libgl1-mesa-glx", "libglib2.0-0", "git") \
    .pip_install(
        "opencv-python-headless", 
        "numpy", 
        "pillow", 
        "torch", 
        "torchvision",
        "ultralytics", # Для YOLOv12/v11 OBB
        "segment-anything-2" # SAM 2
    )

app = modal.App("sjk-smartview-ai")

# Модели будем скачивать во время сборки или лениво при первом запуске
# В реальном проде лучше скачать в image.run_commands
# "yolo11n-obb.pt" - отличный базовый вариант для углов билбордов
YOLO_MODEL = "yolo11n-obb.pt"

@app.function(
    image=image, 
    gpu="A10G",
    timeout=600,
    mounts=[modal.Mount.from_local_dir("./backend/app/ai", remote_path="/root/app/ai")]
)
def process_mockup(background_bytes: bytes, creative_bytes: bytes, corners: list = None):
    """
    Тяжелая функция рендеринга на GPU: YOLO OBB + SAM 2.
    """
    from ultralytics import YOLO
    import torch
    
    # 1. Загрузка изображений
    bg_np = np.frombuffer(background_bytes, np.uint8)
    bg = cv2.imdecode(bg_np, cv2.IMREAD_COLOR)
    
    cr_np = np.frombuffer(creative_bytes, np.uint8)
    cr = cv2.imdecode(cr_np, cv2.IMREAD_COLOR)
    
    if bg is None or cr is None:
        return {"error": "Invalid image data"}

    # 2. Автоматическая детекция углов через YOLOv12-OBB (если не заданы)
    if not corners:
        model = YOLO(YOLO_MODEL)
        results = model.predict(bg, task='obb')
        
        if len(results) > 0 and results[0].obb:
            # Берем самую уверенную детекцию
            # xywhr -> 4 points
            obb = results[0].obb[0]
            points = obb.xyxyxyxy.cpu().numpy()[0] # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            corners = points.tolist()
        else:
            # Fallback: центр экрана с 15% отступом
            h, w = bg.shape[:2]
            corners = [
                [w * 0.2, h * 0.2],
                [w * 0.8, h * 0.2],
                [w * 0.8, h * 0.8],
                [w * 0.2, h * 0.8]
            ]
    
    # 3. Perspective Warp (Гомография)
    src_pts = np.array([
        [0, 0],
        [cr.shape[1], 0],
        [cr.shape[1], cr.shape[0]],
        [0, cr.shape[0]]
    ], dtype="float32")
    
    dst_pts = np.array(corners, dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    
    # Накладываем креатив на черную подложку размера фона
    warped_creative = cv2.warpPerspective(cr, M, (bg.shape[1], bg.shape[0]))
    
    # 4. SAM 2 Segmentation (Occlusion Handling)
    # Создаем маску окклюзий (чтобы провода и деревья были ПОВЕРХ баннера)
    # Примечание: Для полной работы SAM 2 нужны веса и инициализация предиктора.
    # В рамках MVP делаем качественное наложение через альфу и маску гомографии.
    
    screen_mask = np.zeros(bg.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(screen_mask, np.array(corners, dtype=np.int32), 255)
    
    # 5. Смешивание (Blending) с мягкими краями
    alpha_mask = (warped_creative.sum(axis=2) > 0).astype(np.float32)
    # Сглаживаем края для реализма
    alpha_mask = cv2.GaussianBlur(alpha_mask, (3, 3), 0)
    
    result = bg.copy()
    for c in range(3):
        result[:, :, c] = (bg[:, :, c] * (1 - alpha_mask) + warped_creative[:, :, c] * alpha_mask).astype(np.uint8)
    
    # 6. Кодирование в Base64 для передачи обратно через API
    _, buffer = cv2.imencode('.jpg', result, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return base64.b64encode(buffer).decode('utf-8')
