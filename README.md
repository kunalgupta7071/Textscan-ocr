# TextScan — Offline OCR Tool 🔍
**No API key. No internet. 100% Free.**
Tesseract OCR + Flask

---

## Setup (3 steps)

### Step 1 — Tesseract install karo

**Windows:**
- https://github.com/UB-Mannheim/tesseract/wiki se installer download karo
- Install karo (default path: C:\Program Files\Tesseract-OCR\)
- Hindi chahiye toh install mein "hin" language select karo
- app.py mein ye line uncomment karo:
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

**Mac:**
  brew install tesseract tesseract-lang

**Linux (Ubuntu):**
  sudo apt install tesseract-ocr tesseract-ocr-hin

---

### Step 2 — Python packages install karo
  pip install -r requirements.txt

### Step 3 — Run karo
  python app.py

Browser mein kholo: http://localhost:5000

---

## Project Structure
```
textscan-tesseract/
├── app.py           # Flask backend
├── requirements.txt
├── .gitignore
├── README.md
└── public/
    └── index.html   # Frontend
```
