import uuid
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def seed_db():
    db = SessionLocal()
    
    # Check if we already have locations
    existing_locations = db.query(models.Location).count()
    if existing_locations > 0:
        print(f"Database already has {existing_locations} locations. Skipping seed.")
        return

    # Sample Locations
    locations = [
        {
            "name": "Arbat Billboard",
            "category": "Digital Billboard",
            "address": "ul. Arbat, 1, Moscow",
            "coords_lat": 55.7521,
            "coords_lng": 37.5999,
            "primary_photo_url": "https://shojiki.ru/upload/iblock/c38/c3866509930e17634f165e381676f141.jpg",
            "aspect_ratio": 1.77
        },
        {
            "name": "Crocus City Hall Screen",
            "category": "Indoor Media",
            "address": "65-66 km MKAD, Krasnogorsk",
            "coords_lat": 55.8242,
            "coords_lng": 37.3912,
            "primary_photo_url": "https://geofeed.ru/files/media/screen_crocus_city.jpg",
            "aspect_ratio": 2.39
        },
        {
            "name": "Novy Arbat LED",
            "category": "Digital Billboard",
            "address": "Novy Arbat Ave, 24, Moscow",
            "coords_lat": 55.7525,
            "coords_lng": 37.5902,
            "primary_photo_url": "https://www.outdoor.ru/upload/iblock/5d7/5d7f1e7a5c8e3a4e9b7f5e5a5e5a5e5a.jpg",
            "aspect_ratio": 1.77
        }
    ]

    for loc_data in locations:
        location = models.Location(
            id=uuid.uuid4(),
            **loc_data
        )
        db.add(location)
    
    # Create a test manager
    test_user = db.query(models.User).filter(models.User.email == "manager@shojiki.ru").first()
    if not test_user:
        user = models.User(
            id=uuid.uuid4(),
            email="manager@shojiki.ru",
            password_hash="pbkdf2:sha256:260000$test", # Placeholder
            full_name="Константин В.",
            role="manager"
        )
        db.add(user)

    db.commit()
    print("Database seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_db()
