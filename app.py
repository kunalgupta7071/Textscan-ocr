import os
import io
import json
import easyocr
from PIL import Image, ImageFilter, ImageEnhance
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public')

# EasyOCR Readers
reader_en = easyocr.Reader(['en'])
reader_both = easyocr.Reader(['en', 'hi'])

def preprocess_image(img):
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)

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
    mode = request.form.get("mode", "plain")

    raw = file.read()

    if len(raw) > 10 * 1024 * 1024:
        return jsonify({"error": "File 10MB se badi hai"}), 400

    try:
        img = Image.open(io.BytesIO(raw))
        img = preprocess_image(img)

        if lang_key == "eng":
            result_data = reader_en.readtext(img)
        else:
            result_data = reader_both.readtext(img)

        text = "\n".join([item[1] for item in result_data]).strip()

        if not text:
            return jsonify({"error": "Koi text nahi mila. Image clear hai?"}), 200

        if mode == "plain":
            result = text

        elif mode == "structured":
            lines = [l for l in text.split("\n") if l.strip()]
            result = "\n".join(
                f"• {l}" if not l.startswith("•") else l
                for l in lines
            )

        elif mode == "summary":
            lines = [l for l in text.split("\n") if l.strip()]
            words = text.split()

            result = (
                text +
                "\n\n---\n"
                f"📊 Summary:\n"
                f"• Total words: {len(words)}\n"
                f"• Total lines: {len(lines)}\n"
                f"• First line: {lines[0] if lines else '-'}\n"
            )

        elif mode == "json":
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("✓ EasyOCR Loaded")
    print(f"✓ TextScan running → http://localhost:{port}")

    app.run(host="0.0.0.0", port=port, debug=False)
