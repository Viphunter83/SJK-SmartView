# Детальный технический дизайн SJK SmartView

![Mobile App Mockup](/Users/apple/.gemini/antigravity/brain/2386ceb8-f2da-457d-9cdd-17fec96a510d/sjk_smartview_app_mockup_1776067059041.png)

## 0. Оптимизация ресурсов (5 Мб креативы)
Для работы с тяжелыми файлами (5 Мб и выше) на мобильных устройствах, мы внедрим:
*   **Client-side Optimization**: Автоматический ресайз изображения до 2048px по длинной стороне перед отправкой на сервер. Это снизит вес до ~1-1.5 Мб без потери качества для мокапа.
*   **Progressive Upload**: Индикатор загрузки с превью в низком разрешении.

## 1. Схема базы данных (PostgreSQL)

Для MVP нам потребуется 3 основных таблицы:

```sql
-- Пользователи (Сотрудники Shojiki)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
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

## 2. API Спецификация (FastAPI)

### Auth
- `POST /api/v1/auth/login` -> `{ access_token, user }`

### Locations
- `GET /api/v1/locations` -> `List[Location]` (с фильтром по GPS)
- `GET /api/v1/locations/{id}`

### Processing (Core)
- `POST /api/v1/generate`
  - **Body (Multipart)**:
    - `creative`: File (Image)
    - `background`: File (Optional - для Street Photo)
    - `location_id`: UUID (Optional - для выбора из каталога)
  - **Response**: `{ mockup_id, result_url, confidence_score }`

### Типы экранов (на базе каталога Shojiki.vn)
В систему будут заложены пресеты для:
*   **Outdoor LED** (например, Terra Royal, Quận 3).
*   **3D LED** (Nguyen Hue - требует учета искажений для 3D-эффекта).
*   **Стандартные Билборды** (14x8м).
*   **Indoor LCD** (торговые центры Vincom/Lotte).

---

## 3. AI Пайплайн обработки (The Magic)

Пайплайн на бэкенде (Python) будет состоять из следующих шагов:

1.  **Normalization**: Приведение загруженного креатива к нужному aspect ratio экрана ( cropping или padding).
2.  **Detection (YOLOv12-OBB)**: Поиск экрана на фоне. Если это "Street Photo", модель ищет прямоугольник с наибольшей уверенностью.
3.  **Segmentation (SAM 3)**:
    - Подается "промпт" в виде найденного прямоугольника экрана.
    - SAM 3 вырезает всё, что находится *перед* экраном (листья, столбы).
4.  **Homography**: Трансформация креатива под углы, найденные на шаге 2.
5.  **Blending**:
    - Слой 0: Исходное фото.
    - Слой 1: Трансформированный креатив.
    - Слой 2: Инвертированная маска перекрытий из шага 3.
6.  **Relighting (LightGlue / ControlNet)**: Подстройка яркости и цветового баланса баннера под освещение на фото.

---

## 4. План реализации PWA

*   **Camera API**: Использование `input type="file" capture="environment"` для прямого доступа к камере на iOS/Android.
*   **Offline Mode**: Кэширование списка `locations` и их миниатюр через Service Worker.
*   **Progressive Loading**: Отображение "скелетонов" и индикаторов прогресса AI-генерации (Lottie-анимации рабочего процесса).

---

## Дальнейшие шаги
1.  **Создание миграций базы данных** (Supabase/PostgreSQL).
2.  **Инициализация проекта Next.js 15** (Frontend).
3.  **Инициализация FastAPI** (AI Backend).

> [!IMPORTANT]
> На этом этапе мы можем переходить к реализации первого модуля — **Каталога локаций**, если дизайн и спецификации утверждены.
