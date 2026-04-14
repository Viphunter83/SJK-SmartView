import pytest
import os
import cv2
from pathlib import Path

@pytest.fixture
def sample_bg_bytes():
    # Use relative path from backend/tests
    base_path = Path(__file__).parent
    bg_path = base_path / "data" / "sample_bg.png"
    with open(bg_path, "rb") as f:
        return f.read()

@pytest.fixture
def sample_creative_bytes():
    base_path = Path(__file__).parent
    cr_path = base_path / "data" / "sample_creative.png"
    with open(cr_path, "rb") as f:
        return f.read()

@pytest.fixture
def sample_corners():
    # Adjusted corners for the generated billboard in sample_bg.png
    return [
        [430, 95],
        [740, 95],
        [740, 505],
        [430, 505]
    ]
