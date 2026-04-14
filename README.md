# SJK SmartView: AI Mockup Engine for DOOH (Shojiki Group, Vietnam)

![Production Status](https://img.shields.io/badge/Status-Live-success)
![System](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-blue)

SJK SmartView — это специализированная B2B SaaS платформа для **Shojiki Group (Вьетнам)**, предназначенная для мгновенной генерации фотореалистичных мокапов наружной рекламы.

## 🔗 Live Operations
- **Production URL**: [https://sjk-smart-view.vercel.app](https://sjk-smart-view.vercel.app)
- **API Status**: [https://sjk-smartview-production.up.railway.app/api/v1/health](https://sjk-smartview-production.up.railway.app/api/v1/health)

## 🚀 Основные возможности
*   **Premium AI Pipeline (Native)**: Использование **Gemini 3 Pro Image (Nano Banana Pro)** для фотореалистичной гармонизации и нативного вписывания креативов через SCHEMA-инструкции.
*   **Local Rendering Engine (OpenCV)**: Мгновенная трансформация перспективы (Homography) на стороне сервера, используемая как высококачественный черновик и fallback-режим.
*   **No-Mock Data Integrity**: Реальный каталог из 160+ премиальных локаций Shojiki во Вьетнаме (Diamond Plaza, Terra Royal и др.).
*   **Expert AI Architecture**: Полный отказ от внешних GPU-кластеров в пользу прямого многомодального инжиниринга.

## 🛠 Технологический стек
- **Frontend**: Next.js 15 (Vercel), Tailwind CSS, Firebase Auth.
- **Backend API**: FastAPI (Railway), PostgreSQL, Firebase Admin SDK.
- **AI Engine**: **Gemini 3 Pro Image (Native SCHEMA)** + OpenCV (Local Draft).
- **Core Library**: `google-genai` (Multimodal Part-based Logic).

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
- [PWA Installation Guide](docs/user/PWA_INSTALLATION_GUIDE.md) — инструкция по установке приложения.
- [Deployment Guide](docs/deployment/RAILWAY_VERCEL_DEPLOYMENT.md) — инструкция по развертыванию.
- [Business Logic](docs/analysis/business_logic.md) — описание работы системы и AI-пайплайна.

---
*Developed for Shojiki Group Vietnam. 2026 Stable Release.*
