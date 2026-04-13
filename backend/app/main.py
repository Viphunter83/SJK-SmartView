import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import GenerationResponse

app = FastAPI(title="SJK SmartView API", version="0.1.0")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "SJK SmartView API Dispatcher is ready"}

@app.post("/v1/mockup/generate", response_model=GenerationResponse)
async def generate_mockup(
    background: UploadFile = File(...),
    creative: UploadFile = File(...),
    location_id: str = Form(...)
):
    """
    Основной воркер для генерации мокапа.
    Принимает фоновое фото и файл баннера.
    """
    start_time = time.time()
    
    try:
        # 1. Валидация типов
        if not background.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Background must be an image")
        
        # 2. Логика диспетчера:
        # В реальной версии здесь будет вызов Modal.com функций
        # background_bytes = await background.read()
        # creative_bytes = await creative.read()
        
        # Симуляция работы AI воркера
        time.sleep(2) 
        
        # 3. Возврат результата
        # Заглушка: возвращаем URL первого фото как результат
        return GenerationResponse(
            status="completed",
            mockup_url="https://images.unsplash.com/photo-1517430816045-df4b7de11d1d", 
            processing_time=round(time.time() - start_time, 2)
        )
        
    except Exception as e:
        return GenerationResponse(
            status="failed",
            error=str(e),
            processing_time=round(time.time() - start_time, 2)
        )
