import google.generativeai as genai
import os

# Paste your key here again
os.environ["GOOGLE_API_KEY"] = "AIzaSyCTVJrw4BGCGceS4H09hf4AYK0rUVm5tT0"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("🔍 Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")