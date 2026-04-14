# SJK SmartView: AI Mockup Engine for DOOH (Shojiki Group, Vietnam)

![Production Status](https://img.shields.io/badge/Status-Live-success)
![System](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-blue)

SJK SmartView — это специализированная B2B SaaS платформа для **Shojiki Group (Вьетнам)**, предназначенная для мгновенной генерации фотореалистичных мокапов наружной рекламы.

## 🔗 Live Operations
- **Production URL**: [https://sjk-smart-view.vercel.app](https://sjk-smart-view.vercel.app)
- **API Status**: [https://sjk-smartview-production.up.railway.app/api/v1/health](https://sjk-smartview-production.up.railway.app/api/v1/health)

## 🚀 Основные возможности
*   **Premium AI Pipeline**: Использование **Gemini 3 Pro Image** для фотореалистичной гармонизации и наложения креативов.
*   **Local Rendering Engine**: Собственный движок на базе OpenCV для мгновенной перспективы (Homography) без задержек холодного старта GPU.
*   **No-Mock Data Integrity**: Реальный каталог из 160+ премиальных локаций Shojiki во Вьетнаме.
*   **Enterprise Security**: Полная изоляция секретов, интеграция с Firebase Auth и Storage (Сингапур).

## 🛠 Технологический стек
- **Frontend**: Next.js 15 (Vercel), Tailwind CSS, Firebase Auth.
- **Backend API**: FastAPI (Railway), **Production PostgreSQL**, Firebase Admin SDK.
- **AI Computing**: Local CPU (OpenCV) + Gemini AI (Google Cloud).
- **Architecture**: Unified Backend Service (Local-First rendering).

## 📦 Быстрый запуск
1. Подготовьте файл `.env` на основе примера.
2. Положите ключ `service_account.json` в `backend/app/`.
3. Запустите систему:
   ```bash
   docker compose up --build -d
   ```

## 📖 Документация
Подробная информация находится в папке `docs/`:
- [Handover Session](docs/analysis/handover_session.md) — актуальный статус и финализация.
- [Deployment Guide](docs/deployment/RAILWAY_VERCEL_DEPLOYMENT.md) — инструкция по развертыванию.
- [Business Logic](docs/analysis/business_logic.md) — описание работы системы и AI-пайплайна.

---
*Developed for Shojiki Group Vietnam. 2026 Stable Release.*
