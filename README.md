# SJK SmartView: AI Mockup Engine for DOOH (Shojiki Group, Vietnam)

SJK SmartView — это специализированная B2B SaaS платформа для Shojiki Group (Вьетнам), предназначенная для мгновенной генерации фотореалистичных мокапов наружной рекламы.

## 🚀 Основные возможности
*   **Hybrid AI Pipeline**: Использование YOLOv11 OBB на Modal GPU для высокоточной перспективы.
*   **Fast Fallback**: Клиентский рендеринг на Mesh-сетке 20×20 для работы без интернета или GPU.
*   **Vietnam Catalog**: Встроенная база рекламных конструкций Хошимина и Ханоя.
*   **PWA Ready**: Удобная работа на смартфонах и планшетах "в полях".

## 🛠 Технологический стек
- **Frontend**: Next.js 15, Tailwind CSS, Firebase Auth.
- **Backend**: FastAPI, PostgreSQL, Firebase Admin SDK.
- **AI Computing**: Modal.com (GPU Worker), OpenCV, YOLOv11.
- **Infrastructure**: Docker Compose, Firebase Storage.

## 📦 Быстрый запуск
1. Подготовьте файл `.env` на основе примера.
2. Положите ключ `service_account.json` в `backend/app/`.
3. Запустите систему:
   ```bash
   docker compose up --build -d
   ```

## 📖 Документация
Подробная информация находится в папке `docs/analysis/`:
- [Handover Session](docs/analysis/handover_session.md) — актуальное состояние проекта.
- [Business Logic](docs/analysis/business_logic.md) — описание работы системы и AI-пайплайна.
- [Security Standards](docs/analysis/security_standards.md) — правила работы с секретами.
- [Detailed Design](docs/analysis/detailed_design.md) — техническая архитектура и API.

---
*Developed for Shojiki Group Vietnam*
