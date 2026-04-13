import modal
import os
import json

os.environ["MODAL_TOKEN_ID"] = "ak-EFKt0Z21WepTKKUxKfYHdY"
os.environ["MODAL_TOKEN_SECRET"] = "as-h10v9Bc4xPvjb5cp444IoZ"

try:
    print("Looking up modal function...")
    func = modal.Function.lookup("sjk-smartview-ai", "process_mockup")
    print("Function found:", func)
    print("Ready!")
except Exception as e:
    print("Error:", e)
