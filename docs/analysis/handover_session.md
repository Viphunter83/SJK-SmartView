# Handover: SJK SmartView (Production Readiness Edition)

Этот документ фиксирует финальное состояние проекта после успешного вывода в Production на Railway и Vercel, а также полной стабилизации базы данных и AI-пайплайна.

## 1. Текущий статус проекта (Verified 13.04.2026)
*   **Стадия:** СИСТЕМА ЗАПУЩЕНА В ПРОДАКШЕН.
*   **Production URLs:**
    *   Frontend: [https://sjk-smart-view.vercel.app](https://sjk-smart-view.vercel.app)
    *   Backend API: [https://sjk-smartview-production.up.railway.app](https://sjk-smartview-production.up.railway.app)
*   **Data Integrity (No-Mock):** База данных полностью очищена от тестовых данных. Все 160+ локаций — реальные объекты Shojiki Group во Вьетнаме (Terra Royal, Diamond Plaza и др.).
*   **Infrastructure:**
    *   **Railway**: Хостинг бэкенда в регионе `asia-southeast1`.
    *   **PostgreSQL**: Продакшн-база связана через внутреннюю сеть Railway.
    *   **AI Pipeline**: Modal GPU активен и корректно обрабатывает запросы на наложение (homography).

## 2. Ключевые исправления этой сессии
*   **Connectivity Fix:** Решена проблема 404/CORS путем исправления протокола `https://` в переменной `NEXT_PUBLIC_API_URL` на Vercel.
*   **DB Linkage:** Исправлен автоматический маппинг `DATABASE_URL` в Railway для перехода с SQLite (local) на PostgreSQL (production).
*   **CORS Hardening:** Список `ALLOWED_ORIGINS` на бэкенде ограничен только официальным доменом Vercel и localhost.
*   **Auto-Seeding:** Реализован механизм автоматического наполнения пустой БД реальными данными при первом запуске (main.py lifespan).

## 3. Архитектурный стек (Production)
| Слой | Технология | Конфигурация |
|------|------------|--------------|
| **Frontend** | Next.js (Vercel) | Static-Dynamic Hybrid, env-only config. |
| **Backend** | FastAPI (Railway) | Dockerized, region `asia-southeast1`. |
| **Database** | PostgreSQL | Managed Railway Instance. |
| **AI Workload** | Modal API | Python, YOLOv11-OBB, OpenCV. |
| **Storage** | Firebase | Bucket `sjk-smartview.firebasestorage.app`. |

## 4. Гайд по поддержке
*   **Добавление локаций:** Через `app/seed_vietnam.py` (запуск скрипта локально с продакшн `DATABASE_URL`) или напрямую через API.
*   **Логи:** В дашборде Railway сервис `SJK-SmartView`.
*   **Пересборка:** Пуш в ветку `main` GitHub-репозитория автоматически обновляет оба сервиса.

## 5. Контактные данные
*   **Владелец:** Shojiki Group (Vietnam).
*   **Бот-ассистент:** Antigravity (Google DeepMind).

🎉 **Проект готов к эксплуатации отделом продаж Shojiki.**
