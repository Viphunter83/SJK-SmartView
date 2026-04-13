# Детальный технический дизайн SJK SmartView

![Mobile App Mockup](/Users/apple/.gemini/antigravity/brain/2386ceb8-f2da-457d-9cdd-17fec96a510d/sjk_smartview_app_mockup_1776067059041.png)

## 0. Оптимизация ресурсов (5 Мб креативы)
Для работы с тяжелыми файлами (5 Мб и выше) на мобильных устройствах, мы внедрим:
*   **Client-side Optimization**: Автоматический ресайз изображения до 2048px по длинной стороне перед отправкой на сервер. Это снизит вес до ~1-1.5 Мб без потери качества для мокапа.
*   **Progressive Upload**: Индикатор загрузки с превью в низком разрешении.

## 1. Схема базы данных (PostgreSQL)

Для MVP нам потребуется 3 основных таблицы:

```sql
-- Пользователи (Клиентская часть через Firebase Auth)
-- В БД хранятся расширенные данные профиля, если необходимо
CREATE TABLE users (
    id UUID PRIMARY KEY, -- UUID из Firebase UID
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'manager',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Локации (Адреса экранов)
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL, -- Название, например "LED Screen - Nguyen Hue"
    description TEXT,
    coords GEOGRAPHY(POINT), -- Координаты для карты
    primary_photo_url TEXT, -- Базовое "идеальное" фото
    screen_geometry JSONB, -- [x,y] координаты 4 углов на primary_photo
    physical_aspect_ratio FLOAT, -- Соотношение сторон экрана (напр. 1.77 для 16:9)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Мокапы (История генераций)
CREATE TABLE mockups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id), -- Может быть NULL для "Street Photo"
    creative_url TEXT NOT NULL, -- Ссылка на баннер клиента
    result_url TEXT, -- Ссылка на готовый JPEG
    metadata JSONB, -- Данные AI (углы, уверенность модели)
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. API Спецификация

### Auth (Firebase)
- **Client**: `signInWithEmailAndPassword` через Firebase SDK.
- **Backend Access**: Токен проверяется через Firebase Admin SDK в middleware.

### Proxy & Utils
- **Next.js Proxy**: `GET /api/image-proxy?url=...`
  - Решает проблему CORS для клиентского рендерера (текстуры).
  - Стримит изображение с целевого URL (напр. Firebase Storage) с корректными заголовками.

### Processing (Core)
- `POST /api/v1/generate`
  - **Body (Multipart)**:
    - `creative`: Файл баннера.
    - `background`: Файл фото (для "Street Photo").
    - `location_id`: UUID (для выбора из каталога).
  - **Logic**: Если `background` отсутствует, берется `primary_photo_url` из БД локации.
  - **AI Engine**: Вызов `modal_gpu` воркера.

---

## 3. AI Пайплайн и Рендеринг (Implementation Details)

### Backend (Production Path)
1.  **Detection (YOLOv11-OBB)**: Модель обучена на поиск ориентированных рамок (4 точки).
2.  **Homography Transformation**: Вычисление матрицы перехода от прямоугольного баннера к найденному четырехугольнику.
3.  **Alpha Blending**: Наложение баннера на исходное фото с учетом прозрачности и освещенности.

### Frontend (Fallback Path)
1.  **Mesh Triangulation**: Разделение области экрана на сетку 20×20 треугольников.
2.  **Texture Mapping**: Использование Canvas API для отрисовки каждого треугольника с учетом искажений. Это обеспечивает высокую производительность и плавность на мобильных устройствах.

---

## 4. PWA и Мобильная оптимизация (Реализовано)

*   **Manifest**: `public/manifest.json` настроен для работы в режимеStandalone.
*   **Assets**: Сгенерированы иконки 192x192 и 512x512.
*   **Camera API**: Поддерживается захват изображения с камеры через стандартную шторку ОС.

---

## 5. Безопасность и Инфраструктура
*   **Isolation**: Все API-ключи хранятся в переменных окружения.
*   **Access Control**: Firebase Storage защищен правилами (Security Rules), разрешающими запись только аутентифицированным менеджерам.
*   **Deployment**: Система контейнеризирована через Docker Compose для легкого деплоя на любые облака.
