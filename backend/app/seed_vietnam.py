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
            # Горизонтальный широкоформатный экран
            "screen_geometry": [
                {"x": 120, "y": 140},
                {"x": 680, "y": 130},
                {"x": 690, "y": 420},
                {"x": 110, "y": 430},
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
            # Экран на фасаде здания, слегка наклонён
            "screen_geometry": [
                {"x": 200, "y": 80},
                {"x": 620, "y": 90},
                {"x": 630, "y": 390},
                {"x": 190, "y": 400},
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
            # Широкий панорамный экран
            "screen_geometry": [
                {"x": 50,  "y": 160},
                {"x": 750, "y": 145},
                {"x": 755, "y": 440},
                {"x": 45,  "y": 455},
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
            "screen_geometry": [
                {"x": 150, "y": 100},
                {"x": 660, "y": 110},
                {"x": 650, "y": 410},
                {"x": 160, "y": 400},
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
            "screen_geometry": [
                {"x": 180, "y": 120},
                {"x": 640, "y": 115},
                {"x": 645, "y": 400},
                {"x": 175, "y": 405},
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
            "screen_geometry": [
                {"x": 100, "y": 130},
                {"x": 700, "y": 125},
                {"x": 705, "y": 430},
                {"x": 95,  "y": 435},
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
