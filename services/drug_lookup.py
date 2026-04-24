from config import get_db_connection
import re


def extract_dosage(text):
    if not text:
        return "N/A"

    doses = re.findall(r"\d+\s*mg", text.lower())
    return " + ".join(doses) if doses else "Standard dose"


def search_drug(name):

    conn = get_db_connection()
    cursor = conn.cursor()

    name = name.lower().strip()

    result = None

    # 🔥 FIXED: combo detection
    is_combo_input = "+" in name

    # -----------------------------
    # STEP 1: EXACT MATCH (BRAND)
    # -----------------------------
    cursor.execute("""
        SELECT * FROM drugs_1mg
        WHERE LOWER(drug_name) = ?
        LIMIT 1
    """, (name,))

    row = cursor.fetchone()

    # -----------------------------
    # STEP 2: GENERIC MATCH (SMART)
    # -----------------------------
    if not row:
        cursor.execute("""
            SELECT * FROM drugs_1mg
            WHERE LOWER(generic_name) LIKE ?
        """, (f"%{name}%",))

        rows = cursor.fetchall()

        best_match = None

        # 🔥 preferred adult doses
        PREFERRED_DOSES = ["500mg", "650mg", "400mg", "250mg"]

        for r in rows:

            generic = (r["generic_name"] or "").lower()
            dosage = (r["dosage"] or "").lower()

            # ❌ skip combo drugs if single drug input
            if not is_combo_input and "+" in generic:
                continue

            # ✅ exact generic match → highest priority
            if generic.strip() == name:
                best_match = r
                break

            # ✅ prefer adult dose
            if any(d in dosage for d in PREFERRED_DOSES):
                best_match = r

        if best_match:
            row = best_match

    # -----------------------------
    # STEP 3: SAFE FALLBACK
    # -----------------------------
    if not row:
        cursor.execute("""
            SELECT * FROM drugs_1mg
            WHERE LOWER(drug_name) LIKE ?
            LIMIT 1
        """, (f"{name}%",))

        row = cursor.fetchone()

    # -----------------------------
    # FORMAT RESULT
    # -----------------------------
    if row:
        result = {
            "drug_name": row["drug_name"],
            "generic_name": row["generic_name"],
            "uses": row["uses"],
            "dosage": row["dosage"] if row["dosage"] else "Standard dose",
            "side_effects": row["side_effects"],
            "status": "found"
        }
    else:
        result = {
            "drug_name": name,
            "generic_name": name,
            "status": "not_found"
        }

    # -----------------------------
    # DEBUG
    # -----------------------------
    print("🔍 INPUT:", name)
    print("🔍 MATCHED:", result["drug_name"])
    print("🔍 GENERIC:", result["generic_name"])
    print("💊 DOSAGE:", result.get("dosage"))

    conn.close()
    return result