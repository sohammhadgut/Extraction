from flask import Flask, render_template, request, jsonify, send_file
import os, json, requests as http_requests

from utils.preprocess import preprocess_image
from utils.ocr import extract_text
from utils.database import (
    save_database, load_database,
    save_diagram_record, get_all_diagrams,
    activate_diagram, delete_diagram,
    load_label_config, init_label_config, update_label_config,
    delete_label_from_config
)
from utils.build_keywords import build_keyword_dictionary

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(os.path.join(UPLOAD_FOLDER, "diagram_uploads"), exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL   = "claude-sonnet-4-20250514"


@app.route("/")
def home():
    return render_template("index.html")


# ── UPLOAD DIAGRAM → EXTRACT LABELS ─────────────────────────────
@app.route("/upload_diagram", methods=["POST"])
def upload_diagram():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    diagram_name = request.form.get("diagram_name", "").strip()
    if not diagram_name:
        diagram_name = os.path.splitext(file.filename)[0].replace("_", " ").title()

    save_path = os.path.join(UPLOAD_FOLDER, "diagram_uploads", file.filename)
    file.save(save_path)

    processed_path = preprocess_image(save_path)
    raw_labels     = extract_text(processed_path)

    if not raw_labels:
        return jsonify({"message": "No labels detected. Try a clearer image.", "keywords": {}})

    keyword_db   = build_keyword_dictionary(raw_labels, diagram_name=diagram_name)
    record       = save_diagram_record(diagram_name, save_path, raw_labels, keyword_db)
    label_config = init_label_config(keyword_db, replace=True)

    return jsonify({
        "message":      f"'{diagram_name}' extracted — {len(keyword_db)} labels found",
        "diagram_id":   record["id"],
        "diagram_name": diagram_name,
        "total_labels": len(keyword_db),
        "raw_labels":   raw_labels,
        "keywords":     keyword_db,
        "label_config": label_config
    })


# ── GET LABEL CONFIG ─────────────────────────────────────────────
@app.route("/get_label_config", methods=["GET"])
def get_label_config():
    config = load_label_config()
    kw_db  = load_database()
    for label in kw_db:
        if label not in config:
            config[label] = {"keywords": kw_db[label]}
    return jsonify(config)


# ── SAVE EDITED LABELS / KEYWORDS ────────────────────────────────
@app.route("/save_label_edits", methods=["POST"])
def save_label_edits():
    updates = (request.json or {}).get("updates", [])
    if not updates:
        return jsonify({"error": "No updates provided"}), 400
    config = update_label_config(updates)
    return jsonify({"message": "Saved successfully.", "label_config": config})


# ── DELETE SINGLE LABEL ──────────────────────────────────────────
@app.route("/delete_label", methods=["POST"])
def delete_label_route():
    label = (request.json or {}).get("label")
    if not label:
        return jsonify({"error": "label required"}), 400
    delete_label_from_config(label)
    return jsonify({"message": f"'{label}' deleted."})


# ── SAVED DIAGRAMS LIST ──────────────────────────────────────────
@app.route("/get_diagrams", methods=["GET"])
def get_diagrams():
    return jsonify(get_all_diagrams())


@app.route("/activate_diagram", methods=["POST"])
def activate_diagram_route():
    diagram_id = (request.json or {}).get("diagram_id")
    if not diagram_id:
        return jsonify({"error": "diagram_id required"}), 400
    if not activate_diagram(diagram_id):
        return jsonify({"error": "Diagram not found"}), 404
    config = load_label_config()
    return jsonify({"message": "Diagram loaded.", "label_config": config})


@app.route("/delete_diagram", methods=["POST"])
def delete_diagram_route():
    diagram_id = (request.json or {}).get("diagram_id")
    if not diagram_id:
        return jsonify({"error": "diagram_id required"}), 400
    if not delete_diagram(diagram_id):
        return jsonify({"error": "Diagram not found"}), 404
    return jsonify({"message": "Diagram deleted."})


# ── SERVE IMAGES ─────────────────────────────────────────────────
@app.route("/uploads_serve/<path:filepath>")
def serve_upload(filepath):
    full = os.path.join(os.getcwd(), filepath)
    if os.path.exists(full):
        return send_file(full)
    return jsonify({"error": "File not found"}), 404


# ── AI KEYWORD GENERATION ────────────────────────────────────────
def _claude_keywords(label, diagram_name=""):
    context = f" in a '{diagram_name}' diagram" if diagram_name else ""
    prompt = (
        f"For the science diagram label '{label}'{context}, "
        f"list ALL synonyms, alternate names, common names, short forms, "
        f"abbreviations, and chemical/molecular formulas. "
        f"Include: full scientific name, layman name, formula, short code "
        f"(e.g. trachea=windpipe, CO2=carbon dioxide, LA=left atrium, "
        f"soma=cell body, H2O=water). "
        f"Return ONLY a JSON array of lowercase strings. No markdown, no explanation."
    )
    try:
        resp = http_requests.post(
            CLAUDE_API_URL,
            headers={"Content-Type": "application/json"},
            json={"model": CLAUDE_MODEL, "max_tokens": 400,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=15
        )
        if resp.status_code != 200:
            return None
        text = resp.json()["content"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        kws  = json.loads(text)
        if isinstance(kws, list):
            result = [k.strip() for k in kws if k.strip()]
            if label.lower() not in [k.lower() for k in result]:
                result.insert(0, label)
            return result
    except Exception:
        pass
    return None


@app.route("/generate_keywords_ai", methods=["POST"])
def generate_keywords_ai():
    data         = request.json or {}
    diagram_name = data.get("diagram_name", "")

    if "label" in data:
        kws = _claude_keywords(data["label"], diagram_name) or [data["label"]]
        return jsonify({"label": data["label"], "keywords": kws})

    labels = data.get("labels", [])
    if not labels:
        return jsonify({"error": "Provide 'label' or 'labels'"}), 400

    results = {}
    for lbl in labels:
        results[lbl] = _claude_keywords(lbl, diagram_name) or [lbl]
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)
