import re


def normalize_text(text):
    """
    Normalize text for use as a dictionary KEY or for fuzzy matching.
    Keeps digits so formulas work: H2O→h2o, CO2→co2, O2→o2.

    NOTE: This is NOT applied to keyword values — those stay readable.
    Only used for: dictionary keys, matching, deduplication.
    """
    text = str(text).lower().strip()
    text = text.replace("-", "").replace(" ", "")
    # Keep letters and digits, remove everything else
    text = re.sub(r'[^a-z0-9]', '', text)
    return text
