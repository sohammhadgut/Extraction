import json, os, re
from datetime import datetime

KEYWORDS_FILE = "answer_keywords.json"
DIAGRAMS_FILE = "diagrams_store.json"
CONFIG_FILE   = "label_config.json"


# ── ACTIVE KEYWORD DB ────────────────────────────────────────────

def load_database():
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, "r") as f:
        return json.load(f)

def save_database(data):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ── LABEL CONFIG ─────────────────────────────────────────────────

def load_label_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_label_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def init_label_config(keyword_db, replace=False):
    """Build label config from keyword_db. replace=True wipes old config first."""
    existing = {} if replace else load_label_config()
    for label, keywords in keyword_db.items():
        if label not in existing:
            existing[label] = {"keywords": keywords}
    save_label_config(existing)
    return existing

def update_label_config(updates):
    """
    Apply edits from frontend editor.
    updates = [{ "label": "retina", "keywords": ["retina", "retinal layer"] }, ...]
    """
    config = load_label_config()
    for item in updates:
        label = item.get("label", "").strip()
        if not label:
            continue
        raw_kw = item.get("keywords", [])
        if isinstance(raw_kw, str):
            raw_kw = [k.strip() for k in raw_kw.split(",") if k.strip()]
        config[label] = {"keywords": raw_kw}

    save_label_config(config)
    # Sync active keyword DB
    save_database({lbl: cfg["keywords"] for lbl, cfg in config.items()})
    return config

def delete_label_from_config(label):
    config = load_label_config()
    if label in config:
        del config[label]
        save_label_config(config)
        save_database({lbl: cfg["keywords"] for lbl, cfg in config.items()})
        return True
    return False


# ── DIAGRAMS STORE ───────────────────────────────────────────────

def load_diagrams_store():
    if not os.path.exists(DIAGRAMS_FILE):
        return []
    with open(DIAGRAMS_FILE, "r") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []

def save_diagrams_store(diagrams):
    with open(DIAGRAMS_FILE, "w") as f:
        json.dump(diagrams, f, indent=4)

def _make_id(name):
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return f"{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def save_diagram_record(name, image_path, raw_labels, keyword_db):
    diagrams = load_diagrams_store()
    record = {
        "id":         _make_id(name),
        "name":       name,
        "image_path": image_path,
        "raw_labels": raw_labels,
        "keyword_db": keyword_db,
        "saved_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    diagrams.append(record)
    save_diagrams_store(diagrams)
    save_database(keyword_db)
    return record

def get_all_diagrams():
    return [
        {
            "id":          d["id"],
            "name":        d["name"],
            "image_path":  d.get("image_path", ""),
            "raw_labels":  d["raw_labels"],
            "label_count": len(d.get("keyword_db", {})),
            "saved_at":    d["saved_at"]
        }
        for d in load_diagrams_store()
    ]

def load_diagram_by_id(diagram_id):
    for d in load_diagrams_store():
        if d["id"] == diagram_id:
            return d
    return None

def activate_diagram(diagram_id):
    record = load_diagram_by_id(diagram_id)
    if not record:
        return False
    save_database(record["keyword_db"])
    init_label_config(record["keyword_db"], replace=True)
    return True

def delete_diagram(diagram_id):
    diagrams = load_diagrams_store()
    filtered = [d for d in diagrams if d["id"] != diagram_id]
    if len(filtered) == len(diagrams):
        return False
    save_diagrams_store(filtered)
    return True
