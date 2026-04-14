import os
import io
import time
from PIL import Image
from google import genai
from google.genai import types

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Missing GEMINI_API_KEY")
        return
        
    client = genai.Client(api_key=api_key)
    
    # Create valid dummy images
    bg = Image.new('RGB', (1024, 768), color='blue')
    cr = Image.new('RGB', (800, 600), color='red')
    
    bg_io = io.BytesIO()
    bg.save(bg_io, format='JPEG', quality=85)
    bg_bytes = bg_io.getvalue()
    
    cr_io = io.BytesIO()
    cr.save(cr_io, format='JPEG', quality=85)
    cr_bytes = cr_io.getvalue()
    
    bg_part = types.Part.from_bytes(data=bg_bytes, mime_type='image/jpeg')
    cr_part = types.Part.from_bytes(data=cr_bytes, mime_type='image/jpeg')
    
    prompt = "Integrate the creative asset (Image 2) onto the billboard in the background (Image 1)."
    
    print("Sending request...")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, bg_part, cr_part],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(aspect_ratio="16:9")
            )
        )
        print("SUCCESS:", response)
    except Exception as e:
        print("ERROR:", str(e))

if __name__ == "__main__":
    main()
