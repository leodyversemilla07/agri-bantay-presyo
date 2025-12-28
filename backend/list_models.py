from google import genai
from app.core.config import settings

def list_models():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    print("Listing available models...")
    try:
        # The new SDK has a different way to list models
        for m in client.models.list():
            print(f"Model: {m.name}, Name: {m.display_name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
