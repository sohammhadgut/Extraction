"""
ocr.py
──────
Key fixes:
1. Nearby bounding boxes on the same line are merged
   → "Outer" + "Membrane" becomes "Outer Membrane"
   → "Carbon" + "Dioxide" becomes "Carbon Dioxide"
2. Unicode subscripts normalised before processing
   → H₂O → H2O,  CO₂ → CO2,  O₂ → O2,  CH₂O → CH2O
3. Formula tokens kept whole (digits allowed in output)
"""

import easyocr
import cv2
import re
import unicodedata

reader = easyocr.Reader(['en'], gpu=False)

MIN_CONF     = 0.25   # lower threshold — formulas often score lower
MERGE_X_GAP  = 80     # max pixel gap between two boxes to merge (same line)
MERGE_Y_DIFF = 22     # max vertical centre difference to count as same line

# ── SUBSCRIPT / UNICODE FIX ──────────────────────────────────────
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SUP = str.maketrans("⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "+-0123456789")

def _fix_unicode(text):
    text = text.translate(_SUB).translate(_SUP)
    return unicodedata.normalize("NFKC", text)


# ── BOUNDING BOX HELPERS ─────────────────────────────────────────
def _cy(bbox):   return sum(p[1] for p in bbox) / 4
def _cx(bbox):   return sum(p[0] for p in bbox) / 4
def _left(bbox): return min(p[0] for p in bbox)
def _right(bbox):return max(p[0] for p in bbox)


# ── VALIDITY ─────────────────────────────────────────────────────
def _valid(text, conf):
    if conf < MIN_CONF:                          return False
    if not text.strip():                         return False
    if sum(c.isalpha() for c in text) < 1:      return False  # needs ≥1 letter
    if re.fullmatch(r'[^a-zA-Z0-9]+', text):    return False  # pure symbols
    return True


# ── MERGE NEARBY BOXES ───────────────────────────────────────────
def _merge(detections):
    """
    Join bounding boxes that sit close together on the same horizontal line.
    Fixes multi-word labels being split by EasyOCR.
    """
    if not detections:
        return []

    # Sort top→bottom, left→right
    dets  = sorted(detections, key=lambda d: (_cy(d[0]), _cx(d[0])))
    used  = [False] * len(dets)
    out   = []

    for i, (bi, ti, ci) in enumerate(dets):
        if used[i]:
            continue
        group_text  = ti
        group_conf  = ci
        group_right = _right(bi)
        group_cy    = _cy(bi)
        group_cx    = _cx(bi)
        used[i]     = True

        # Look ahead for boxes on same line that are close by
        for j, (bj, tj, cj) in enumerate(dets):
            if used[j]:
                continue
            cy_j   = _cy(bj)
            left_j = _left(bj)

            same_line  = abs(cy_j - group_cy) <= MERGE_Y_DIFF
            close_next = 0 <= (left_j - group_right) <= MERGE_X_GAP

            if same_line and close_next:
                group_text  = group_text + " " + tj
                group_conf  = min(group_conf, cj)
                group_right = _right(bj)
                used[j]     = True

        out.append((None, group_text.strip(), group_conf))

    return out


# ── MAIN ─────────────────────────────────────────────────────────
def extract_text(image_path):
    """
    Extract labels from a diagram image.
    Returns deduplicated list of clean label strings.
    """
    image = cv2.imread(image_path)
    if image is None:
        return []

    raw = reader.readtext(image)

    # Fix unicode/subscripts on every token first
    fixed = [(bbox, _fix_unicode(text.strip()), conf) for bbox, text, conf in raw]

    # Merge nearby boxes
    merged = _merge(fixed)

    # Deduplicate and filter
    seen, result = set(), []
    for (_, text, conf) in merged:
        text = text.strip()
        if not _valid(text, conf):
            continue
        key = re.sub(r'\s+', '', text.lower())
        if key not in seen:
            seen.add(key)
            result.append(text)

    return result
