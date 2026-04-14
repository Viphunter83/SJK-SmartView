"""
SJK SmartView API — Dispatcher
FastAPI backend for AI-powered DOOH mockup generation.
"""
# load_dotenv MUST be first
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import time
import uuid
import base64
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.schemas import GenerationResponse, LocationInfo, MockupHistoryItem, CornerDetectionResponse, Point
from app.database import engine, get_db, SessionLocal
from app import models
from app.storage import storage_service
from app.seed_vietnam import seed_vietnam
from app.ai import processor # Локальный AI-процессор (OpenCV + Gemini)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Lifespan & Startup
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check if database is empty and seed if necessary
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(models.Location).count()
        if count == 0:
            logger.info("Database is empty. Seeding real Shojiki Group locations...")
            seed_vietnam()
        else:
            logger.info(f"Database already has {count} locations.")
    except Exception as e:
        logger.error(f"Error during startup seeding: {e}")
    finally:
        db.close()
    yield
    # Shutdown logic

# ─────────────────────────────────────────────────────────────
# AI Pipeline (Gemini 3 Pro Native)
# ─────────────────────────────────────────────────────────────
print("AI Pipeline: Gemini 3 Pro Native Active (SCHEMA v4.0 Ready) ✓")

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
    version="1.0.0",
    description="AI Dispatcher for DOOH mockup generation — Shojiki Group Vietnam",
    lifespan=lifespan
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
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "sjk-smartview-api"}

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "version": "1.0.0",
        "service": "SJK SmartView API",
        "ai_pipeline": "local_engine",
        "ai_model": "Gemini 3 Pro Image model",
        "status": "online",
    }

@app.get("/api/v1/health", tags=["Health"])
async def api_health_check():
    return {
        "status": "healthy",
        "ai_available": True,
        "ai_model": "Gemini 3 Pro Image (Native SCHEMA v4.0)",
        "engine": "nano_banana_pro",
    }

@app.post("/api/v1/admin/reseed", tags=["Admin"])
async def admin_reseed(db: Session = Depends(get_db)):
    """Force re-seed database with updated screen geometry coordinates."""
    try:
        seed_vietnam()
        count = db.query(models.Location).count()
        return {"status": "success", "message": f"Re-seeded {count} locations with corrected geometry"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    Использует локальный OpenCV процессор.
    """
    try:
        contents = await image.read()
        result = processor.detect_corners_local(contents)
        
        corners_pts = [Point(x=float(p[0]), y=float(p[1])) for p in result["corners"]]
        
        return CornerDetectionResponse(
            corners=corners_pts,
            confidence=0.9,
            message="Углы определены через локальный OpenCV-движок",
            method="opencv_local"
        )
    except Exception as e:
        logger.error(f"Detection error: {e}")
        # Возвращаем стандартные углы (15% отступ) как безопасный дефолт
        return CornerDetectionResponse(
            corners=[Point(x=100, y=100), Point(x=700, y=100), Point(x=700, y=500), Point(x=100, y=500)],
            confidence=0.5,
            message=f"Ошибка детекции: {e}. Применен стандартный охват.",
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
    corners_json: Optional[str] = Form(None),
    result_url: Optional[str] = Form(None),  # Client-side canvas result URL
    use_premium: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Генерация мокапа.

    Режим 1 (Canvas): result_url уже готов от клиента — просто сохраняем в историю.
    Режим 2 (Standard): Perspective Warp + CV Blending.
    Режим 3 (Premium): Gemini 3 SCHEMA Inpainting + Harmonization.
    """
    start_time = time.time()
    current_mode = "standard"
    if use_premium:
        current_mode = "premium"
    elif result_url:
        current_mode = "canvas"

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
                    raw = loc.screen_geometry
                    print(f"DEBUG: Location found: {loc.name}, Raw geometry type: {type(raw)}")
                    
                    if raw:
                        # Если это строка (иногда бывает при чтении из некоторых драйверов)
                        if isinstance(raw, str):
                            import json
                            raw = json.loads(raw)
                            
                        if isinstance(raw, list) and len(raw) > 0:
                            if isinstance(raw[0], dict):
                                corners = [[float(p["x"]), float(p["y"])] for p in raw]
                            elif isinstance(raw[0], (list, tuple)):
                                corners = [list(p) for p in raw]
                    
                    print(f"DEBUG: Parsed corners from DB: {corners}")
            except Exception as e:
                print(f"ERROR: Failed to parse location geometry: {e}")
        
        # Если кастомная локация (или углов в БД нет), но пользователь выбрал точки вручную
        if not corners and corners_json:
            import json
            try:
                parsed_corners = json.loads(corners_json)
                if isinstance(parsed_corners, list) and len(parsed_corners) == 4:
                    corners = [[p["x"], p["y"]] for p in parsed_corners]
            except Exception as e:
                print(f"Warning: Failed to parse corners_json: {e}")

        # Загружаем креатив в хранилище
        creative_storage_url = await storage_service.upload_file(
            cr_bytes, creative.filename or "creative.jpg",
            content_type=creative.content_type or "image/jpeg",
            folder="creatives"
        )

        processing_time = round(time.time() - start_time, 2)
        status = "completed"
        final_result_url = result_url  # Клиентский canvas результат (Вариант Б)

        # Вариант А: Стационарный рендеринг (Native AI Engine)
        if bg_bytes and not result_url:
            try:
                if use_premium:
                    logger.info("Using Premium AI: Gemini 3 Pro Native (Thinking: HIGH)")
                    result_bytes = await processor.process_mockup_premium(bg_bytes, cr_bytes, corners)
                else:
                    logger.info("Using Standard AI: OpenCV Perspective Local")
                    result_bytes = processor.process_mockup_standard(bg_bytes, cr_bytes, corners)

                final_result_url = await storage_service.upload_file(
                    result_bytes, "result.jpg",
                    content_type="image/jpeg",
                    folder="results"
                )
                processing_time = round(time.time() - start_time, 2)

            except Exception as e:
                logger.error(f"Local generation failed ({current_mode}): {e}")
                status = "failed"

        if not final_result_url:
            status = "failed"

        # Сохраняем в историю
        new_mockup = models.Mockup(
            location_id=db_location_id,
            creative_url=creative_storage_url,
            result_url=final_result_url,
            status=status,
            metadata_json={"processing_time": processing_time, "mode": current_mode}
        )
        db.add(new_mockup)
        db.commit()

        return GenerationResponse(
            status=status,
            mockup_url=final_result_url,
            processing_time=processing_time,
            mode=current_mode
        )

    except Exception as e:
        db.rollback()
        print(f"generate_mockup error: {e}")
        return GenerationResponse(
            status="failed",
            error=str(e),
            processing_time=round(time.time() - start_time, 2)
        )
