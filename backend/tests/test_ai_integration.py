import pytest
import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ai import processor
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

def test_opencv_standard_processing(sample_bg_bytes, sample_creative_bytes, sample_corners):
    """
    Verifies that the standard OpenCV-based perspective warp works correctly.
    """
    result = processor.process_mockup_standard(
        sample_bg_bytes, 
        sample_creative_bytes, 
        sample_corners
    )
    assert isinstance(result, bytes)
    assert len(result) > 0
    print(f"Standard processing successful, output size: {len(result)} bytes")

@pytest.mark.asyncio
async def test_gemini_premium_connectivity():
    """
    Verifies that the Gemini API key is valid and the model can be reached.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key is not None, "GEMINI_API_KEY must be set in .env"
    assert api_key.startswith("AIza"), "Invalid Gemini API Key format"
    
    client = genai.Client(api_key=api_key)
    
    # Verify that we can reach the premium model
    try:
        # Use the premium model for a simple text response to verify access
        response = client.models.generate_content(
            model='gemini-3-pro-image-preview', 
            contents="Connectivity test. Reply 'OK'."
        )
        assert response.text is not None
        print(f"Gemini Premium model ({'gemini-3-pro-image-preview'}) connectivity verified.")
    except Exception as e:
        pytest.fail(f"Gemini Premium API connection failed: {e}")

@pytest.mark.asyncio
async def test_full_premium_flow(sample_bg_bytes, sample_creative_bytes, sample_corners):
    """
    Tests the end-to-end premium flow (OpenCV + Gemini call).
    Verifies that the premium result is distinct from the standard result,
    indicating that AI processing actually occurred.
    """
    # 1. Get standard result
    standard_result = processor.process_mockup_standard(
        sample_bg_bytes,
        sample_creative_bytes,
        sample_corners
    )
    
    # 2. Get premium result (Real AI call)
    premium_result = await processor.process_mockup_premium(
        sample_bg_bytes,
        sample_creative_bytes,
        sample_corners
    )

    assert premium_result is not None
    assert isinstance(premium_result, bytes)
    assert len(premium_result) > 1000
    
    # If the API actually processed it, it should be binary-different from the standard draft
    # (provided the API call succeeded and didn't just fallback)
    assert premium_result != standard_result, "Premium result should be enhanced by AI and different from standard draft"
    print("Full premium flow verified (Real AI Integration).")
