def clean_uses(text):
    if not text:
        return "General therapeutic use"

    # remove 'Treatment of'
    text = text.replace("Treatment of", "")
    text = text.replace("treatment of", "")

    # fix spacing
    text = text.strip()

    # remove leading commas
    text = text.lstrip(", ").strip()

    # split into parts
    parts = [p.strip() for p in text.split(",") if p.strip()]

    # keep only first 2 for readability
    return ", ".join(parts[:2]) if parts else "General therapeutic use"


def clean_side_effects(side):
    if not side:
        return "Minimal"

    # ensure list
    if isinstance(side, str):
        side = side.split()

    # clean + limit
    cleaned = [s.strip() for s in side if s.strip()]

    return ", ".join(cleaned[:4]) if cleaned else "Minimal"


def format_drug(d):

    name = d.get("drug_name", "Unknown")

    uses = clean_uses(d.get("uses", ""))
    dosage = d.get("dosage", "") or "Standard dose"
    side = clean_side_effects(d.get("side_effects", []))

    return {
        "drug_name": name,
        "summary": f"Used for {uses}",
        "dosage": dosage,
        "side_effects": side
    }