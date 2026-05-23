"""
build_keywords.py
─────────────────
KEY FIX: Keywords stored as READABLE strings, not normalized.
  - "wind pipe" stays "wind pipe"
  - "H2O" stays "H2O"
  - "esophagus" appears as a synonym of "trachea" clearly

The normalized key is only used as the dictionary key for lookup.
The values (keywords) stay readable for display and fuzzy matching.
"""

from utils.keyword_generator import generate_related_words
from utils.normalize import normalize_text


def build_keyword_dictionary(labels, diagram_name=""):
    """
    Args:
        labels:       raw OCR strings e.g. ["Outer Membrane", "H2O", "Calvin Cycle"]
        diagram_name: context for Claude e.g. "Photosynthesis"

    Returns:
        { normalized_key: [readable_keyword, readable_keyword, ...] }
    """
    keyword_db = {}
    seen_keys  = set()

    for label in labels:
        original = label.strip()
        if not original:
            continue

        # Normalize only for the key (deduplication + lookup)
        key = normalize_text(original)
        if len(key) < 2 or key in seen_keys:
            continue
        seen_keys.add(key)

        # Pass ORIGINAL readable label to Claude for best context
        keywords = generate_related_words(original, diagram_name=diagram_name)

        # Always include original readable form in keywords
        kw_set = []
        seen_kw = set()
        for k in keywords:
            kl = k.lower().strip()
            if kl not in seen_kw:
                seen_kw.add(kl)
                kw_set.append(k)

        if original.lower() not in seen_kw:
            kw_set.insert(0, original)

        keyword_db[key] = kw_set

    return keyword_db
