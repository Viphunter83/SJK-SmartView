"""
Seed script: Vietnam localization — 6 реальных экранов Shojiki Group.
Запуск: python -m app.seed_vietnam (из директории backend/)
"""
import uuid
import os
import sys

# Добавляем путь для запуска как скрипта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine
from app import models

# Убеждаемся что таблицы созданы
models.Base.metadata.create_all(bind=engine)


def seed_vietnam():
    db = SessionLocal()

    # 1. Очистить старые локации
    db.query(models.Location).delete()
    db.commit()
    print("Old locations cleared.")

    # 2. Реальные экраны SJK Group (данные с shojiki.vn)
    # screen_geometry: примерные углы (List[Point]) для перспективного наложения
    # x, y — нормализованные координаты относительно изображения 800x600
    locations = [
        # ─── HO CHI MINH CITY ───────────────────────────────────────
        {
            "name": "Terra Royal LED Screen",
            "category": "Outdoor Digital",
            "address": "83 Lý Chính Thắng, Quận 3, HCMC",
            "coords_lat": 10.7853,
            "coords_lng": 106.6852,
            "primary_photo_url": "https://shojiki.vn/template/uploads/2021/07/quang-cao-led-ngoai-troi-nga-tu-ly-chinh-thang-nam-ky-khoi-nghia-7.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            # Вертикальный экран в верхне-правой части снимка (1500x1125)
            "screen_geometry": [
                {"x": 296, "y":  32},
                {"x": 459, "y":  29},
                {"x": 461, "y": 248},
                {"x": 293, "y": 251},
            ],
        },
        {
            "name": "20 Nguyen Hue 3D LED",
            "category": "3D Digital",
            "address": "20 Nguyễn Huệ, Quận 1, HCMC",
            "coords_lat": 10.7745,
            "coords_lng": 106.7031,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/11/man-hinh-led-20-nguyen-hue-2.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            # Оранжевый SJK в верхне-центральной части (1330x996)
            "screen_geometry": [
                {"x": 168, "y":  18},
                {"x": 469, "y":  15},
                {"x": 472, "y": 238},
                {"x": 165, "y": 241},
            ],
        },
        {
            "name": "KFC Le Lai Intersection",
            "category": "3D Digital",
            "address": "78 Lê Lai, Quận 1, HCMC (Phu Dong Cross)",
            "coords_lat": 10.7712,
            "coords_lng": 106.6945,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/06/pepsi-chay-quang-cao-tren-man-hinh-led-kfc-quan-1.jpg",
            "aspect_ratio": 2.39,
            "is_active": True,
            # Широкий баннер Pepsi над KFC (960x640)
            "screen_geometry": [
                {"x": 162, "y":  38},
                {"x": 725, "y":  28},
                {"x": 729, "y": 314},
                {"x": 158, "y": 323},
            ],
        },
        # ─── HANOI ──────────────────────────────────────────────────
        {
            "name": "Ham Ca Map (Shark Fin) Hanoi",
            "category": "3D Digital",
            "address": "1-13 Đinh Tiên Hoàng, Hoàn Kiếm, Hanoi",
            "coords_lat": 21.0315,
            "coords_lng": 105.8524,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/04/led-ham-ca-map-ban-dem-6.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            # Фото не загружается (1382 bytes) — используем центральные координаты
            "screen_geometry": [
                {"x": 200, "y": 100},
                {"x": 600, "y":  95},
                {"x": 605, "y": 350},
                {"x": 195, "y": 355},
            ],
        },
        {
            "name": "VTV Building Screen",
            "category": "Outdoor Digital",
            "address": "43 Nguyễn Chí Thanh, Ba Đình, Hanoi",
            "coords_lat": 21.0264,
            "coords_lng": 105.8112,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2021/08/led-vtv-43-nguyen-chi-thanh-ha-noi-2.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            # Горизонтальный экран VietinBank, центр-лево (1432x1053)
            "screen_geometry": [
                {"x": 148, "y": 145},
                {"x": 422, "y": 142},
                {"x": 425, "y": 262},
                {"x": 145, "y": 265},
            ],
        },
        {
            "name": "Vincom Ba Trieu LED",
            "category": "Outdoor Digital",
            "address": "191 Bà Triệu, Hai Bà Trưng, Hanoi",
            "coords_lat": 21.0112,
            "coords_lng": 105.8491,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2023/01/led-ba-trieu-ha-noi-1.jpeg",
            "aspect_ratio": 1.77,
            "is_active": True,
            # Экран Nova на крыше, верх-слева (1907x1065)
            "screen_geometry": [
                {"x": 166, "y":  25},
                {"x": 329, "y":  23},
                {"x": 331, "y": 155},
                {"x": 164, "y": 158},
            ],
        },
    ]

    for loc_data in locations:
        location = models.Location(id=uuid.uuid4(), **loc_data)
        db.add(location)

    db.commit()
    print(f"Vietnam seeding completed: {len(locations)} locations added.")
    db.close()


if __name__ == "__main__":
    seed_vietnam()
