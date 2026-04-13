## Current Production Status (Verified 13.04.2026)

- **Frontend (Vercel)**: [https://sjk-smart-view.vercel.app](https://sjk-smart-view.vercel.app)
- **Backend API (Railway)**: [https://sjk-smartview-production.up.railway.app](https://sjk-smartview-production.up.railway.app)
- **Database (PostgreSQL)**: Connected via Railway Internal Networking.
- **AI Pipeline**: Active (Modal GPU + OpenCV Fallback).
- **Region**: `asia-southeast1` (Singapore) for optimal Vietnam latency.

---

## Часть 1. Развертывание Backend (Railway)

Railway идеально подходит для нашего FastAPI + PostgreSQL бэкенда.

### 1. Подготовка Railway
1. Зарегистрируйтесь / Авторизуйтесь на [Railway.app](https://railway.app/).
2. В дашборде нажмите **"New Project"** -> **"Deploy from GitHub repo"**.
3. Выберите репозиторий `SJK SmartView`.

### 2. Автоматическая сборка
Railway автоматически обнаружит файл `railway.json` в корне проекта и поймет, что нужно использовать `backend/Dockerfile`. Вам **не нужно** вручную менять Root Directory в настройках.

### 3. База данных (PostgreSQL)
1. Нажмите **"New"** -> **"Database"** -> **"Add PostgreSQL"**.
2. Railway автоматически создаст БД.
3. Вернитесь к настройкам сервиса вашего приложения (бэкенда), перейдите в **Variables**.
4. Railway сам предложит привязать базу (сгенерирует `DATABASE_URL`). Согласитесь, или добавьте вручную `DATABASE_URL = ${{PostgreSQL.DATABASE_URL}}`.

### 4. Переменные окружения (Environment Variables)
Во вкладке **Variables** бэкенда добавьте следующие ключи:

| Ключ | Значение | Описание |
|------|----------|----------|
| `PORT` | `8000` | Railway подставляет свой порт, бэкенд настроен слушать `${PORT:-8000}`. |
| `ALLOWED_ORIGINS` | `https://sjk-smart-view.vercel.app,http://localhost:3000` | Должен включать точный домен Vercel **без слэша на конце**. |
| `DATABASE_URL` | `postgresql://...` | Внутренний URL базы `postgres.railway.internal`. |
| `FIREBASE_STORAGE_BUCKET` | `sjk-smartview.firebasestorage.app` | Конфиг стораджа. |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | `{"type": "service_account", ...}` | JSON-ключ в одну строку. |
| `MODAL_TOKEN_ID` | `ak-...` | |
| `MODAL_TOKEN_SECRET` | `as-...` | |

### 5. Получение домена
1. Перейдите во вкладку **Settings** -> **Environment**.
2. В разделе **Public Networking** нажмите **"Generate Domain"**.
3. Railway выдаст вам домен вида `https://web-production-xxx.up.railway.app`. Скопируйте его, он понадобится для Vercel.

---

## Часть 2. Развертывание Frontend (Vercel)

Vercel — оптимальный выбор для нашего приложения на базе Next.js.

### 1. Подготовка Vercel
1. Авторизуйтесь на [Vercel.com](https://vercel.com/).
2. Нажмите **"Add New"** -> **"Project"**.
3. Импортируйте репозиторий `SJK SmartView` из GitHub.

### 2. Настройка проекта
В окне *"Configure Project"*:
1. **Framework Preset**: Выберите `Next.js` (обычно определяется автоматически).
2. **Root Directory**: Нажмите "Edit" и выберите каталог `frontend`.
3. **Build Command**: `npx next build` (оставьте по умолчанию).
4. **Install Command**: `npm install` (оставьте по умолчанию).

### 3. Переменные окружения (Environment Variables)
Разверните секцию **Environment Variables** и добавьте следующие ключи:

| Ключ | Значение | Описание |
|------|----------|----------|
| `NEXT_PUBLIC_API_URL` | `https://sjk-smartview-production.up.railway.app` | **ОБЯЗАТЕЛЬНО с `https://`** и без слэша на конце. |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | `...` | |
| ... | ... | ... |

> [!IMPORTANT]
> Если в `NEXT_PUBLIC_API_URL` забыть `https://`, браузер будет пытаться делать запросы внутри домена Vercel (относительные пути), что приведет к 404.

### 4. Deploy
Нажмите **Deploy**. После успешной сборки Vercel выдаст домен: `https://sjk-smart-view.vercel.app`.

После завершения успешной сборки, Vercel выдаст вам домен вашего приложения, например: `https://sjk-smartview.vercel.app`.

---

## Часть 3. Связка (Завершающий штрих)

Мы должны разрешить доступ Frontend к Backend (чтобы CORS не блокировал запросы).

1. Скопируйте домен, который вам выдал Vercel (например, `https://sjk-smartview.vercel.app`).
2. Вернитесь в настройки Backend сервиса на **Railway**.
3. Во вкладке **Variables** найдите ключ `ALLOWED_ORIGINS`.
4. Замените значение `*` на список через запятую (Production URL и локальный для разработки):
   ```
   https://sjk-smartview.vercel.app, http://localhost:3000
   ```
5. Railway автоматически инициирует новую сборку с новыми переменными.

🎉 **Готово! Проект запущен в Production и полностью безопасен.**
