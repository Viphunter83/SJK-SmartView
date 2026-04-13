from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="SJK SmartView AI Dispatcher")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене ограничить до домена фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SJK SmartView API Dispatcher is running"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/generate")
async def generate_mockup(
    creative: UploadFile = File(...),
    location_id: str = None,
    background: UploadFile = File(None)
):
    # Логика диспетчера ( FastAPI -> Modal/Replicate )
    return {
        "mockup_id": "test-id",
        "status": "processing",
        "message": "Generation started"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
