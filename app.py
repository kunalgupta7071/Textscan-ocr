import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='public')

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✓ TextScan (Browser-based OCR) running → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
