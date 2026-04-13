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
                {"x": 344, "y":  45},
                {"x": 435, "y":  45},
                {"x": 435, "y": 256},
                {"x": 344, "y": 256},
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
                {"x": 310, "y":  25},
                {"x": 472, "y":  14},
                {"x": 475, "y": 226},
                {"x": 307, "y": 238},
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
                {"x": 250, "y": 103},
                {"x": 567, "y": 131},
                {"x": 567, "y": 413},
                {"x": 250, "y": 384},
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
                {"x": 218, "y": 217},
                {"x": 321, "y": 217},
                {"x": 321, "y": 299},
                {"x": 218, "y": 299},
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
                {"x": 138, "y":  65},
                {"x": 223, "y":  65},
                {"x": 224, "y": 175},
                {"x": 136, "y": 177},
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
