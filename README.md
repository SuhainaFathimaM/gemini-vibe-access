
# 🌟 Gemini Vibe Access

**AI-Powered Accessibility Platform for Simplified Text, Sign Language Keywords, and TTS Audio**

Gemini Vibe Access is an accessibility-focused web application that helps users—especially those with dyslexia, visual impairments, cognitive challenges, or reading difficulties—access complex digital text with ease.
It uses **Google Gemini AI**, **React**, **Flask**, and **gTTS** to simplify text, extract keywords for sign language support, and generate audio narration.
A complete multi-modal accessibility tool in one platform.

---

## 🚀 Features

### ✅ **1. Text Simplification**

* Converts complex content into simple text.
* Maintains original meaning while improving readability.
* Works with PDFs, TXT files, and URLs.

### ✅ **2. Keyword Extraction (Sign Language Support)**

* Extracts 5–8 key nouns & verbs.
* Displays them as clickable cards linked to sign-language videos.

### ✅ **3. Text-to-Speech (TTS)**

* Generates natural audio from simplified text using gTTS.
* Audio can be streamed or included in a downloadable ZIP file.

### ✅ **4. Accessibility Modes**

* **Default Mode**
* **Dyslexia Mode** (OpenDyslexic font)
* **High Contrast Mode** for visually impaired users

### ✅ **5. Downloadable Accessibility Pack**

Includes:

* `simplified.txt`
* `keywords.json`
* `audio.mp3`
  (all zipped for offline access)

---

## 🖥️ Tech Stack

### **Frontend**

* React.js
* TailwindCSS
* Axios

### **Backend**

* Python Flask
* pdfplumber
* BeautifulSoup
* Google Generative AI SDK
* gTTS
* Zipfile & secure file handling

### **AI Model**

* **Gemini 3 Pro (gemini-3-pro)**
  Used for text simplification & keyword extraction.

---

## 🧠 System Architecture

```
User Input → Flask API → Text Extraction (PDF/URL/TXT)
          → Gemini AI (Simplify + Keywords)
          → gTTS Audio Generation
          → ZIP Packaging
          → React Frontend Displays Output
```

---

## 📂 Folder Structure

```
Gemini-Vibe-Access/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── uploads/
│
└── README.md
```

---

## 🛠️ Installation & Setup

### **1. Clone the repository**

```bash
git clone https://github.com/SuhainaFathimaM/Gemini-Vibe-Access.git
cd Gemini-Vibe-Access
```

---

## Backend Setup (Flask)

### **2. Create virtual environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Add your Gemini API key**

Create a file:

```
backend/.env
```

Add:

```
GEMINI_API_KEY=your_key_here
```

### **5. Run backend**

```bash
python app.py
```

---

## Frontend Setup (React)

### **6. Install dependencies**

```bash
cd ../frontend
npm install
```

### **7. Start the development server**

```bash
npm start
```

---

# 🔗 API Endpoints

### **POST /process-text**

Input: PDF | TXT | URL
Output: simplified text, keywords, audio file path

Request example:

```json
{
  "type": "url",
  "value": "https://example.com"
}
```

Response:

```json
{
  "simplified_text": "...",
  "keywords": ["word1", "word2"],
  "audio_url": "/static/audio/output.mp3"
}
```

---

# 🏆 Key Strengths

* Built with **accessibility-first design**.
* Solves real problems faced by dyslexic and visually impaired users.
* Provides **multi-modal output** (text + audio + sign language).
* Robust error handling (PDFs, scraping failures, non-JSON AI outputs).

---

# 🧩 Challenges Solved

### **PDF Formatting Issues**

→ Resolved using pdfplumber text extraction.

### **AI sometimes returns messy output**

→ Solved using `safe_parse_ai_json`.

### **Long text issues**

→ Implemented chunking and truncation logic.

### **TTS length limitations**

→ Generated simplified text first to reduce size.

---

# 🎯 Future Enhancements

* Multi-language support.
* Browser extension for live page simplification.
* Better PDF layout preservation (images, tables).
* Offline AI model integration.
* More customization (reading levels, voice controls).

---

# 🤝 Contributing

Contributions are welcome!
To contribute:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Open a Pull Request

---

# 📜 License

This project is licensed under the **MIT License**.

---

# ❤️ Acknowledgments

* Google Gemini
* gTTS
* React community
* Flask community
