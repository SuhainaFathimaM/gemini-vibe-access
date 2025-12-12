# app.py
import os
import json
import re
import zipfile
import tempfile
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import pdfplumber
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GOOGLE_API_KEY = "your_api_key_here"
if not GOOGLE_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY environment variable not set.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

try:
    model = genai.GenerativeModel("models/gemini-flash-latest")
    #model = genai.GenerativeModel("models/gemini-3-pro")
except Exception:
    model = None
    print("⚠️ Could not initialize model object. Ensure google.generativeai is installed and key set.")


def extract_text_from_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print("PDF parse error:", e)
    return text


def extract_text_from_url(url, max_chars=15000):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text().strip() for p in paragraphs)
        return text[:max_chars]
    except Exception as e:
        print("URL fetch error:", e)
        return ""


def extract_json_from_text(text):
    """
    Attempt to find the first JSON object in text.
    """
    try:
        # Remove triple-backtick fenced code blocks if any
        text = text.replace("```json", "").replace("```", "")
        # Find the first '{' ... '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
            return candidate
        # fallback: try to find bracketed list (rare)
        return None
    except Exception:
        return None


def safe_parse_ai_json(ai_text):
    candidate = extract_json_from_text(ai_text)
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # try to fix simple trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", candidate)
        try:
            return json.loads(fixed)
        except Exception:
            return None


@app.route("/")
def home():
    return "✅ Gemini Backend Running"


@app.route("/process", methods=["POST"])
def process():
    try:
        # 1) Get text from file or URL
        text_content = ""
        filename_root = "document"

        if "file" in request.files and request.files["file"].filename != "":
            f = request.files["file"]
            filename = secure_filename(f.filename)
            filename_root = os.path.splitext(filename)[0]
            saved_path = os.path.join(UPLOAD_FOLDER, filename)
            f.save(saved_path)

            if filename.lower().endswith(".pdf"):
                text_content = extract_text_from_pdf(saved_path)
            elif filename.lower().endswith(".txt"):
                with open(saved_path, "r", encoding="utf-8", errors="ignore") as fh:
                    text_content = fh.read()
            else:
                return jsonify({"error": "Unsupported file type (use .pdf or .txt)"}), 400

        elif "url" in request.form and request.form.get("url").strip() != "":
            url = request.form.get("url").strip()
            text_content = extract_text_from_url(url)
            filename_root = re.sub(r"[^a-zA-Z0-9_-]", "_", url)[:40]

        else:
            return jsonify({"error": "No file or url provided"}), 400

        if not text_content or len(text_content.strip()) == 0:
            return jsonify({"error": "Could not extract text from the given input"}), 400

        # Limit text length to avoid huge prompts
        text_for_ai = text_content[:4000]

        # 2) Build a robust prompt asking for JSON only
        prompt = f"""
You are an assistive-technology assistant. Given the TEXT below, output ONLY a valid JSON object (no markdown, no explanations).
The JSON must have these fields:
- "simplified": a simplified version of the text suitable for Grade 5 reading level (short sentences).
- "keywords": a list of 5 to 8 single-word keywords (nouns/verbs) suitable for sign-language lookup.

Return the JSON only.

TEXT:
\"\"\"{text_for_ai}\"\"\"
"""

        ai_text = None
        ai_json = None

        if model is None:
            # If model unavailable, return fallback
            simplified = text_for_ai
            keywords = []
        else:
            # call Gemini model
            try:
                response = model.generate_content(prompt)
                # Many SDKs provide a text field — adapt to library variant
                # try multiple attribute names
                ai_text = getattr(response, "text", None) or getattr(response, "content", None) or str(response)
            except Exception as e:
                print("AI request error:", e)
                ai_text = None

            if ai_text:
                parsed = safe_parse_ai_json(ai_text)
                if parsed:
                    ai_json = parsed
                    simplified = ai_json.get("simplified", text_for_ai)
                    keywords = ai_json.get("keywords", [])
                else:
                    # fallback to using whole ai_text as simplified
                    simplified = ai_text.strip()
                    # try to extract few words by simple heuristics
                    words = re.findall(r"\b[a-zA-Z]{4,}\b", simplified)
                    keywords = list(dict.fromkeys(words))[:6]
            else:
                simplified = text_for_ai
                keywords = []

        # 3) Generate TTS audio (gTTS)
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", filename_root)[:40]
        audio_filename = f"{safe_name}_audio.mp3"
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        try:
            tts = gTTS(simplified, lang="en")
            tts.save(audio_path)
        except Exception as e:
            print("TTS error:", e)
            audio_path = None

        # 4) Create a ZIP with simplified.txt, keywords.json, audio.mp3 (if exists)
        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # simplified text
            zf.writestr(f"{safe_name}_simplified.txt", simplified)
            # keywords JSON
            zf.writestr(f"{safe_name}_keywords.json", json.dumps(keywords, indent=2))
            # audio file
            if audio_path and os.path.exists(audio_path):
                zf.write(audio_path, arcname=audio_filename)

        zip_buf.seek(0)
        zip_filename = f"{safe_name}_accessibility_pack.zip"
        zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
        with open(zip_path, "wb") as f:
            f.write(zip_buf.read())

        # Return response with URLs
        host = request.host_url.rstrip("/")  # e.g. http://127.0.0.1:5000
        audio_url = f"{host}/download/{audio_filename}" if audio_path else None
        zip_url = f"{host}/download/{zip_filename}"

        return jsonify({
            "simplified_text": simplified,
            "keywords": keywords,
            "audio_url": audio_url,
            "zip_url": zip_url,
        })

    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500


@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    safe = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
