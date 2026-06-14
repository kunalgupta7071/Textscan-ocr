import os
import io
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public')

# Windows users ke liye — agar Windows pe run kar rahe ho toh uncomment karo:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

LANG_MAP = {
    "eng":  "eng",
    "hin":  "hin",
    "both": "hin+eng",
    "any":  "eng",   # auto detect nahi hota, eng default
}

def preprocess_image(img):
    """Image quality improve karo OCR ke liye"""
    # Grayscale
    img = img.convert("L")
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    # Contrast enhance
    img = ImageEnhance.Contrast(img).enhance(2.0)
    # Scale up agar chhota hai
    w, h = img.size
    if w < 1000:
        scale = 1000 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img

@app.route("/api/ocr", methods=["POST"])
def ocr():
    if "image" not in request.files:
        return jsonify({"error": "Image nahi mili"}), 400

    file = request.files["image"]
    lang_key = request.form.get("lang", "eng")
    mode     = request.form.get("mode", "plain")

    raw = file.read()
    if len(raw) > 10 * 1024 * 1024:
        return jsonify({"error": "File 10MB se badi hai"}), 400

    try:
        img = Image.open(io.BytesIO(raw))
        img = preprocess_image(img)

        lang = LANG_MAP.get(lang_key, "eng")

        # PSM 6 = assume a single uniform block of text
        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(img, lang=lang, config=config).strip()

        if not text:
            return jsonify({"error": "Koi text nahi mila image mein. Image clear hai?"}), 200

        # Mode ke hisaab se output format
        if mode == "plain":
            result = text

        elif mode == "structured":
            lines = [l for l in text.split("\n") if l.strip()]
            result = "\n".join(f"• {l}" if not l.startswith("•") else l for l in lines)

        elif mode == "summary":
            lines = [l for l in text.split("\n") if l.strip()]
            words = text.split()
            result = (
                text + "\n\n---\n"
                f"📊 Summary:\n"
                f"• Total words: {len(words)}\n"
                f"• Total lines: {len(lines)}\n"
                f"• First line: {lines[0] if lines else '-'}\n"
            )

        elif mode == "json":
            import json
            lines = [l for l in text.split("\n") if l.strip()]
            result = json.dumps({
                "text": text,
                "lines": lines,
                "wordCount": len(text.split()),
                "charCount": len(text)
            }, ensure_ascii=False, indent=2)

        else:
            result = text

        return jsonify({"text": result})

    except pytesseract.TesseractNotFoundError:
        return jsonify({
            "error": "Tesseract install nahi hai! README padho install karne ke liye."
        }), 500
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✓ TextScan (Tesseract) running → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
