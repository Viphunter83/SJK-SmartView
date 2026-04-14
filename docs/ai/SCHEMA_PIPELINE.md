# SCHEMA Expert Methodology: SJK SmartView AI Pipeline

Этот документ описывает методологию **SCHEMA** (*Structured Components for Harmonized Engineered Modular Architecture*), которая используется для управления моделью **Gemini 3 Pro Image (Nano Banana Pro)** в проекте SJK SmartView.

## 1. Концепция
SCHEMA — это не просто промпт, а модульная структура, имитирующая системное мышление инженера. Она переводит модель из режима «творческого рисования» в режим «прецизионной вставки объекта с учетом физики мира».

## 2. Глобальные триггеры
Для активации возможностей Gemini 3 используются следующие управляющие сигналы:

- **Thinking: Enable**: Активирует многошаговый внутренний процесс рассуждения. Модель сначала анализирует геометрию, а затем выполняет рендеринг.
- **Geometric Consistency**: Предписывает 100% сохранение линий и углов оригинальной поверхности.
- **Lighting Harmonization**: Модуль анализа освещения. Модель анализирует источники света на фото фона и накладывает соответствующие блики на рекламный баннер.

## 3. Процесс обработки (Multi-stage Refinement)
1. **Input Part 1 (Background)**: Фото реальной локации Shojiki.
2. **Input Part 2 (Asset)**: Креатив (AD Asset) клиента.
3. **Prompt Execution**:
   - `Identify Surface`: Поиск рекламной поверхности на Part 1.
   - `Calculate Homography`: Нативный расчет перспективной трансформации.
   - `Harmonization`: Бесшовное вписывание с учетом зернистости, теней и текстуры экрана.

## 4. SCHEMA Prompt Structure
Унифицированный промпт состоит из следующих блоков:
```text
[SCHEMA v3.0]
[CONTEXT: DOOH Advertising Professional Integration]
[GOAL: Seamlessly integrate Image 2 into the detected display surface of Image 1]
[TRIGGERS: Thinking, Geometric Consistency, High-Fidelity Harmonization]
[REFINEMENT: 
 - Maintain 100% screen geometry.
 - Inherit ambient lighting from Image 1.
 - Apply subtle micro-shadows on bezels.
]
```

## 5. Преимущества перед классическим CV (OpenCV/YOLO)
- **Умная окклюзия**: Модель автоматически «понимает», если перед экраном находится дерево или столб, и вписывает картинку за препятствие.
- **Фотореализм**: В отличие от простой Homography, которая часто выглядит «наклеенной», SCHEMA создает ощущение, что реклама реально светится на экране.
- **Стабильность**: Отсутствие зависимости от отдельного GPU-воркера снижает риск отказа системы.

---
*Документация актуальна на версию Gemini 3 Pro Image Preview (April 2026).*
