"""
SJK SmartView API — Dispatcher
FastAPI backend for AI-powered DOOH mockup generation.
"""
# load_dotenv MUST be first, before any modal imports
from dotenv import load_dotenv
load_dotenv()

import os
import time
import uuid
import base64
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.schemas import GenerationResponse, LocationInfo, MockupHistoryItem, CornerDetectionResponse, Point
from app.database import engine, get_db
from app import models
from app.storage import storage_service

# ─────────────────────────────────────────────────────────────
# Создание таблиц при запуске
# ─────────────────────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────────────────────
# Modal AI функция (опциональная)
# ─────────────────────────────────────────────────────────────
modal_fn = None        # process_mockup
modal_detect_fn = None  # detect_corners

def _load_modal():
    global modal_fn, modal_detect_fn
    modal_token_id = os.getenv("MODAL_TOKEN_ID")
    modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")
    if not modal_token_id or not modal_token_secret:
        print("Modal: credentials not configured. Using client-side canvas.")
        return
    try:
        import modal
        modal_fn = modal.Function.from_name("sjk-smartview-ai", "process_mockup")
        modal_detect_fn = modal.Function.from_name("sjk-smartview-ai", "detect_corners")
        print("Modal GPU pipeline: connected to 'sjk-smartview-ai' ✓")
    except Exception as e:
        print(f"Modal: connection failed ({e}). Will use OpenCV fallback.")

_load_modal()

# ─────────────────────────────────────────────────────────────
# CORS — читаем из env var
# ─────────────────────────────────────────────────────────────
_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]

# ─────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="SJK SmartView API",
    version="0.4.0",
    description="AI Dispatcher for DOOH mockup generation — Shojiki Group Vietnam"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача загруженных файлов (только для local fallback)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ─────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "version": "0.4.0",
        "service": "SJK SmartView API",
        "ai_pipeline": "modal_gpu" if modal_fn else "client_canvas",
        "modal_connected": modal_fn is not None,
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "ai_available": modal_fn is not None,
        "corner_detection": "modal_yolo_obb" if modal_detect_fn else "opencv",
    }


# ─────────────────────────────────────────────────────────────
# Locations
# ─────────────────────────────────────────────────────────────
@app.get("/api/v1/locations", response_model=List[LocationInfo], tags=["Locations"])
async def get_locations(db: Session = Depends(get_db)):
    """Возвращает все активные локации из каталога."""
    locations = db.query(models.Location).filter(models.Location.is_active == True).all()
    result = []
    for loc in locations:
        # Приводим screen_geometry к унифицированному List[Point]
        geometry = None
        if loc.screen_geometry:
            if isinstance(loc.screen_geometry, list):
                # Уже в нужном формате [{"x":...,"y":...}]
                geometry = [Point(**p) if isinstance(p, dict) else p for p in loc.screen_geometry]
            elif isinstance(loc.screen_geometry, dict) and "corners" in loc.screen_geometry:
                # Старый формат: {"corners": [[x,y],...]}
                raw = loc.screen_geometry["corners"]
                if raw and isinstance(raw[0], list):
                    geometry = [Point(x=c[0], y=c[1]) for c in raw]
                else:
                    geometry = [Point(**c) for c in raw]

        result.append(LocationInfo(
            id=loc.id,
            name=loc.name,
            category=loc.category or "",
            address=loc.address,
            coords_lat=loc.coords_lat,
            coords_lng=loc.coords_lng,
            primary_photo_url=loc.primary_photo_url,
            screen_geometry=geometry,
            aspect_ratio=loc.aspect_ratio or 1.77,
            is_active=loc.is_active if loc.is_active is not None else True,
        ))
    return result


# ─────────────────────────────────────────────────────────────
# Corner Detection
# ─────────────────────────────────────────────────────────────
@app.post("/api/v1/mockup/detect-corners", response_model=CornerDetectionResponse, tags=["AI"])
async def detect_corners(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Автоматически находит 4 угла экрана на фото.
    Использует OpenCV (Canny + Hough) как базовый алгоритм.
    При наличии Modal — использует YOLO OBB.
    """
    contents = await image.read()

    # Если Modal доступен — используем dedicated GPU detect_corners функцию
    if modal_detect_fn:
        try:
            result = modal_detect_fn.remote(contents)
            if result and result.get("corners"):
                raw = result["corners"]
                corners_pts = [Point(x=float(p[0]), y=float(p[1])) for p in raw]
                return CornerDetectionResponse(
                    corners=corners_pts,
                    confidence=result.get("confidence", 0.85),
                    message="Углы определены через YOLO OBB на GPU",
                    method="modal_yolo_obb"
                )
        except Exception as e:
            print(f"Modal detect_corners failed: {e}")

    # OpenCV-based corner detection (работает без GPU)
    try:
        import numpy as np
        import cv2

        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is not None:
            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)

            # Найти контуры и взять самый большой прямоугольный
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            best_corners = None
            max_area = 0

            for cnt in contours:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4:
                    area = cv2.contourArea(approx)
                    if area > max_area and area > (w * h * 0.05):
                        max_area = area
                        best_corners = approx.reshape(4, 2).tolist()

            if best_corners:
                # Сортируем углы: TL, TR, BR, BL
                pts = sorted(best_corners, key=lambda p: p[0] + p[1])
                tl = pts[0]
                br = pts[3]
                remaining = [pts[1], pts[2]]
                tr = min(remaining, key=lambda p: p[1])
                bl = max(remaining, key=lambda p: p[1])

                corners = [
                    Point(x=float(tl[0]), y=float(tl[1])),
                    Point(x=float(tr[0]), y=float(tr[1])),
                    Point(x=float(br[0]), y=float(br[1])),
                    Point(x=float(bl[0]), y=float(bl[1])),
                ]
                return CornerDetectionResponse(
                    corners=corners,
                    confidence=0.75,
                    message="Контур найден через OpenCV",
                    method="opencv"
                )

    except ImportError:
        pass
    except Exception as e:
        print(f"OpenCV corner detection error: {e}")

    # Fallback: разумные дефолтные углы на основе размера изображения
    # Используем 15% отступ от краёв
    try:
        import struct
        # Читаем размер PNG/JPEG без полного декодирования
        if contents[0:4] == b'\xff\xd8\xff\xe0' or contents[0:4] == b'\xff\xd8\xff\xe1':
            # JPEG — берём умный дефолт 800x600
            w, h = 800, 600
        else:
            w, h = 800, 600
    except Exception:
        w, h = 800, 600

    pad_x, pad_y = int(w * 0.15), int(h * 0.15)
    corners = [
        Point(x=pad_x, y=pad_y),
        Point(x=w - pad_x, y=pad_y),
        Point(x=w - pad_x, y=h - pad_y),
        Point(x=pad_x, y=h - pad_y),
    ]
    return CornerDetectionResponse(
        corners=corners,
        confidence=0.3,
        message="Автодетекция недоступна, установлены стандартные углы",
        method="fallback"
    )


# ─────────────────────────────────────────────────────────────
# History
# ─────────────────────────────────────────────────────────────
@app.get("/api/v1/history", response_model=List[MockupHistoryItem], tags=["Mockups"])
async def get_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """История генераций с пагинацией."""
    mockups = (
        db.query(models.Mockup)
        .order_by(models.Mockup.created_at.desc())
        .offset(offset)
        .limit(min(limit, 100))  # max 100 за раз
        .all()
    )

    result = []
    for m in mockups:
        loc_name = "Street Upload"
        if m.location_id:
            loc = db.query(models.Location).filter(models.Location.id == m.location_id).first()
            if loc:
                loc_name = loc.name

        result.append(MockupHistoryItem(
            id=m.id,
            location_name=loc_name,
            creative_url=m.creative_url,
            result_url=m.result_url,
            status=m.status,
            created_at=m.created_at,
            processing_time=m.metadata_json.get("processing_time", 0) if m.metadata_json else 0,
        ))
    return result


@app.delete("/api/v1/history/{mockup_id}", tags=["Mockups"])
async def delete_mockup(mockup_id: str, db: Session = Depends(get_db)):
    """Удалить запись из истории."""
    try:
        uid = uuid.UUID(mockup_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mockup ID")

    mockup = db.query(models.Mockup).filter(models.Mockup.id == uid).first()
    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    db.delete(mockup)
    db.commit()
    return {"status": "deleted"}


# ─────────────────────────────────────────────────────────────
# Generate Mockup
# ─────────────────────────────────────────────────────────────
@app.post("/api/v1/mockup/generate", response_model=GenerationResponse, tags=["AI"])
async def generate_mockup(
    creative: UploadFile = File(...),
    background: Optional[UploadFile] = File(None),
    location_id: str = Form("custom"),
    result_url: Optional[str] = Form(None),  # Client-side canvas result URL
    db: Session = Depends(get_db)
):
    """
    Генерация мокапа.

    Режим 1 (Canvas): result_url уже готов от клиента — просто сохраняем в историю.
    Режим 2 (Modal GPU): вызов удалённого GPU-воркера.
    """
    start_time = time.time()

    try:
        cr_bytes = await creative.read()
        bg_bytes = await background.read() if background else None

        # Определяем локацию
        db_location_id = None
        corners = None

        if location_id != "custom":
            try:
                loc_uuid = uuid.UUID(location_id)
                loc = db.query(models.Location).filter(models.Location.id == loc_uuid).first()
                if loc:
                    db_location_id = loc.id
                    if loc.screen_geometry:
                        raw = loc.screen_geometry
                        if isinstance(raw, list) and raw:
                            if isinstance(raw[0], dict):
                                corners = [[p["x"], p["y"]] for p in raw]
                            elif isinstance(raw[0], list):
                                corners = raw
            except ValueError:
                pass

        # Загружаем креатив в хранилище
        creative_storage_url = await storage_service.upload_file(
            cr_bytes, creative.filename or "creative.jpg",
            content_type=creative.content_type or "image/jpeg",
            folder="creatives"
        )

        processing_time = round(time.time() - start_time, 2)
        status = "completed"
        final_result_url = result_url  # Клиентский canvas результат (Вариант Б)

        # Вариант А: Modal GPU рендеринг
        if modal_fn and bg_bytes and not result_url:
            try:
                raw_result = modal_fn.remote(bg_bytes, cr_bytes, corners)

                # worker.py возвращает base64 строку — декодируем в bytes
                if isinstance(raw_result, str):
                    result_bytes = base64.b64decode(raw_result)
                elif isinstance(raw_result, bytes):
                    result_bytes = raw_result
                else:
                    raise ValueError(f"Unexpected Modal result type: {type(raw_result)}")

                final_result_url = await storage_service.upload_file(
                    result_bytes, "result.jpg",
                    content_type="image/jpeg",
                    folder="results"
                )
                processing_time = round(time.time() - start_time, 2)

            except Exception as e:
                print(f"Modal generation failed: {e}")
                status = "failed"

        if not final_result_url:
            status = "failed"

        # Сохраняем в историю
        new_mockup = models.Mockup(
            location_id=db_location_id,
            creative_url=creative_storage_url,
            result_url=final_result_url,
            status=status,
            metadata_json={"processing_time": processing_time, "mode": "modal" if modal_fn else "canvas"}
        )
        db.add(new_mockup)
        db.commit()

        return GenerationResponse(
            status=status,
            mockup_url=final_result_url,
            processing_time=processing_time
        )

    except Exception as e:
        db.rollback()
        print(f"generate_mockup error: {e}")
        return GenerationResponse(
            status="failed",
            error=str(e),
            processing_time=round(time.time() - start_time, 2)
        )
