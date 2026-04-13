import time
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.schemas import GenerationResponse, LocationInfo, MockupHistoryItem
from app.database import engine, get_db
from app import models
from app.storage import storage_service
from fastapi.staticfiles import StaticFiles

# Создание таблиц при запуске
models.Base.metadata.create_all(bind=engine)
from typing import List, Optional
import uuid

# Импорт Modal функции
try:
    import modal
    f = modal.Function.lookup("sjk-smartview-ai", "process_mockup")
except Exception:
    f = None

app = FastAPI(title="SJK SmartView API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене ограничить!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача статики (для локального fallback)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"status": "online", "message": "SJK SmartView API Dispatcher is ready"}

@app.get("/api/v1/locations", response_model=List[LocationInfo])
async def get_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    return locations

@app.get("/api/v1/history", response_model=List[MockupHistoryItem])
async def get_history(db: Session = Depends(get_db)):
    # Пока возвращаем все мокапы (без фильтра по пользователю для MVP)
    mockups = db.query(models.Mockup).order_by(models.Mockup.created_at.desc()).limit(20).all()
    
    result = []
    for m in mockups:
        loc_name = "Custom / Street"
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
            processing_time=m.metadata_json.get("processing_time", 0) if m.metadata_json else 0
        ))
    return result

@app.post("/v1/mockup/generate", response_model=GenerationResponse)
async def generate_mockup(
    creative: UploadFile = File(...),
    background: Optional[UploadFile] = File(None),
    location_id: str = Form("custom"),
    db: Session = Depends(get_db)
):
    """
    Основной диспетчер для генерации мокапа.
    """
    start_time = time.time()
    
    try:
        # 1. Чтение байтов
        bg_bytes = None
        if background:
            bg_bytes = await background.read()
        
        cr_bytes = await creative.read()
        
        # 2. Определение параметров локации
        corners = None
        db_location_id = None
        
        if location_id != "custom":
            try:
                loc_uuid = uuid.UUID(location_id)
                loc = db.query(models.Location).filter(models.Location.id == loc_uuid).first()
                if loc:
                    db_location_id = loc.id
                    if loc.screen_geometry and "corners" in loc.screen_geometry:
                        corners = loc.screen_geometry["corners"]
                    
                    # Если фоновое фото не прислано, пытаемся взять из БД/URL
                    if not bg_bytes and loc.primary_photo_url:
                        # В реальном приложении здесь был бы вызов к хранилищу
                        # Для MVP: если это URL, воркер может сам его скачать или мы передаем null
                        pass 
            except ValueError:
                pass

        # 3. Вызов Modal AI и сохранение файлов
        creative_url = await storage_service.upload_file(cr_bytes, creative.filename)
        
        mockup_url = None
        status = "completed"
        processing_time = 0

        if f:
            # Вызываем удаленную функцию
            result_data = f.remote(bg_bytes, cr_bytes, corners)
            
            # Сохраняем результат в хранилище (результат от Modal - байты)
            mockup_url = await storage_service.upload_file(result_data, "result.jpg")
            processing_time = round(time.time() - start_time, 2)
        else:
            time.sleep(1) # Имитация
            mockup_url = "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d" 
            status = "completed"
            processing_time = round(time.time() - start_time, 2)

        # 4. Сохранение в историю (Mockups table)
        new_mockup = models.Mockup(
            location_id=db_location_id,
            creative_url=creative_url, 
            result_url=mockup_url,
            status=status,
            metadata_json={"processing_time": processing_time}
        )
        db.add(new_mockup)
        db.commit()

        return GenerationResponse(
            status=status,
            mockup_url=mockup_url, 
            processing_time=processing_time
        )
        
    except Exception as e:
        db.rollback()
        return GenerationResponse(
            status="failed",
            error=str(e),
            processing_time=round(time.time() - start_time, 2)
        )
