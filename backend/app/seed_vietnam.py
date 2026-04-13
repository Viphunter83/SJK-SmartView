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
            "id": "f18921fb-f339-49c9-83bb-c7620cd2d72f",
            "name": "Terra Royal LED Screen",
            "category": "Outdoor Digital",
            "address": "83 Lý Chính Thắng, Quận 3, HCMC",
            "coords_lat": 10.7853,
            "coords_lng": 106.6852,
            "primary_photo_url": "https://shojiki.vn/template/uploads/2021/07/quang-cao-led-ngoai-troi-nga-tu-ly-chinh-thang-nam-ky-khoi-nghia-7.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            "screen_geometry": [
                {"x": 344, "y":  45},
                {"x": 435, "y":  45},
                {"x": 435, "y": 256},
                {"x": 344, "y": 256},
            ],
        },
        {
            "id": "80aa83c2-c4cd-4e2c-9334-fd6e8362398a",
            "name": "20 Nguyen Hue 3D LED",
            "category": "3D Digital",
            "address": "20 Nguyễn Huệ, Quận 1, HCMC",
            "coords_lat": 10.7745,
            "coords_lng": 106.7031,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/11/man-hinh-led-20-nguyen-hue-2.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            "screen_geometry": [
                {"x": 310, "y":  25},
                {"x": 444, "y":  18},
                {"x": 447, "y": 226},
                {"x": 307, "y": 238},
            ],
        },
        {
            "id": "c7726d9c-71f4-4d89-abfe-393527bf2dde",
            "name": "KFC Le Lai Intersection",
            "category": "3D Digital",
            "address": "78 Lê Lai, Quận 1, HCMC (Phu Dong Cross)",
            "coords_lat": 10.7712,
            "coords_lng": 106.6945,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/06/pepsi-chay-quang-cao-tren-man-hinh-led-kfc-quan-1.jpg",
            "aspect_ratio": 2.39,
            "is_active": True,
            "screen_geometry": [
                {"x": 250, "y": 103},
                {"x": 567, "y": 131},
                {"x": 567, "y": 413},
                {"x": 250, "y": 384},
            ],
        },
        # ─── HANOI ──────────────────────────────────────────────────
        {
            "id": "58de7667-b3c4-4b61-8187-51c2fdcc9ba3",
            "name": "Ham Ca Map (Shark Fin) Hanoi",
            "category": "3D Digital",
            "address": "1-13 Đinh Tiên Hoàng, Hoàn Kiếm, Hanoi",
            "coords_lat": 21.0315,
            "coords_lng": 105.8524,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2024/04/led-ham-ca-map-ban-dem-6.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            "screen_geometry": [
                {"x": 200, "y": 150},
                {"x": 600, "y": 150},
                {"x": 600, "y": 450},
                {"x": 200, "y": 450},
            ],
        },
        {
            "id": "d3a8bb24-5ce2-49b8-bd68-dbe58804d7f8",
            "name": "VTV Building Screen",
            "category": "Outdoor Digital",
            "address": "43 Nguyễn Chí Thanh, Ba Đình, Hanoi",
            "coords_lat": 21.0264,
            "coords_lng": 105.8112,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2021/08/led-vtv-43-nguyen-chi-thanh-ha-noi-2.jpg",
            "aspect_ratio": 1.77,
            "is_active": True,
            "screen_geometry": [
                {"x": 218, "y": 217},
                {"x": 321, "y": 217},
                {"x": 321, "y": 299},
                {"x": 218, "y": 299},
            ],
        },
        {
            "id": "bc9e3d1b-8cd2-4055-951d-14c87a896773",
            "name": "Vincom Ba Trieu LED",
            "category": "Outdoor Digital",
            "address": "191 Bà Triệu, Hai Bà Trưng, Hanoi",
            "coords_lat": 21.0112,
            "coords_lng": 105.8491,
            "primary_photo_url": "https://shojiki.vn/wp-content/uploads/2023/01/led-ba-trieu-ha-noi-1.jpeg",
            "aspect_ratio": 1.77,
            "is_active": True,
            "screen_geometry": [
                {"x": 138, "y":  65},
                {"x": 223, "y":  65},
                {"x": 224, "y": 175},
                {"x": 136, "y": 177},
            ],
        },
    ]

    for loc_data in locations:
        loc_id = uuid.UUID(loc_data.pop("id"))
        location = models.Location(id=loc_id, **loc_data)
        db.add(location)

    db.commit()
    print(f"Vietnam seeding completed: {len(locations)} locations added.")
    db.close()


if __name__ == "__main__":
    seed_vietnam()
