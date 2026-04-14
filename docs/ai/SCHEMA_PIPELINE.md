Этот документ описывает методологию **SCHEMA v4.0** (*Structured Components for Harmonized Engineered Modular Architecture*), которая используется для управления моделью **Gemini 3 Pro Image (Nano Banana Pro)** в проекте SJK SmartView.

## 1. Концепция
SCHEMA — это не просто промпт, а модульная структура, имитирующая системное мышление инженера. Она переводит модель из режима «творческого рисования» в режим «прецизионной вставки объекта с учетом физики мира».

## 2. Глобальные триггеры
Для активации возможностей Gemini 3 используются следующие управляющие сигналы:

- **Thinking: HIGH**: Активирует глубокий многошаговый процесс рассуждения. Модель не просто рисует, а строит пространственную модель сцены.
- **Flexible Anchors (Гибкие Якоря)**: Новая концепция v4.0. Мы передаем ИИ примерные координаты (hints), но позволяем ему самостоятельно определять финальные границы для 100% точности.
- **Occlusion Mastery**: Способность модели корректно обрабатывать препятствия перед экраном (деревья, люди, столбы) без масок.

## 3. Процесс обработки (Multi-stage Refinement)
1. **Input Part 1 (Background)**: Фото реальной локации Shojiki.
2. **Input Part 2 (Asset)**: Креатив (AD Asset) клиента.
3. **Prompt Execution**:
   - `Identify Surface`: Поиск рекламной поверхности на Part 1.
   - `Calculate Homography`: Нативный расчет перспективной трансформации.
   - `Harmonization`: Бесшовное вписывание с учетом зернистости, теней и текстуры экрана.

## 4. SCHEMA Prompt Structure
```text
[SCHEMA v4.0: High-Fidelity DOOH Integration]
CONTEXT: Professional advertising mockup for Shojiki Group Vietnam.
TASK: Integrate Image 2 (Asset) into the high-priority display surface found in Image 1 (Environment).

COGNITIVE STEPS:
1. Scene Analysis: Identify primary digital screen/LED surface.
2. Geometric Mapping: Warp Image 2 with perfect perspective.
3. Photorealistic Blending: Inherit lighting, grain, and reflections.
4. Occlusion Handling: Ensure layering behind foreground objects.
```

## 5. Преимущества перед классическим CV (OpenCV/YOLO)
- **Умная окклюзия**: Модель автоматически «понимает», если перед экраном находится дерево или столб, и вписывает картинку за препятствие.
- **Фотореализм**: В отличие от простой Homography, которая часто выглядит «наклеенной», SCHEMA создает ощущение, что реклама реально светится на экране.
- **Стабильность**: Отсутствие зависимости от отдельного GPU-воркера снижает риск отказа системы.

---
*Документация актуальна на версию Gemini 3 Pro Image Preview (April 2026).*
