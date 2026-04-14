import requests
import io
import os
from PIL import Image

bg = Image.new('RGB', (800, 600), color = 'red')
cr = Image.new('RGB', (200, 200), color = 'blue')

bg_bytes = io.BytesIO()
bg.save(bg_bytes, format='JPEG')
cr_bytes = io.BytesIO()
cr.save(cr_bytes, format='JPEG')

print("Sending request to production API...")
res = requests.post(
    "https://sjk-smartview-production.up.railway.app/api/v1/mockup/generate",
    headers={"X-SJK-Key": "e30575eb-cf4e-4304-a008-a9f3cc91cab2"},
    data={
        "location_id": "custom",
        "use_premium": "true",
    },
    files={
        "creative": ("cr.jpg", cr_bytes.getvalue(), "image/jpeg"),
        "background": ("bg.jpg", bg_bytes.getvalue(), "image/jpeg")
    }
)
print("Status:", res.status_code)
print("Response:", res.text)
