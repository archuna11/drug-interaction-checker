from services.drug_lookup import search_drug
from services.formatter import format_drug
from clinical_ddi_check import drug_interaction_check, normalize_medication_names
from services.food_interaction import get_food_interactions
from services.disease_interaction import get_disease_interactions
from services.ai_summary import generate_ai_summary


def run_pipeline(input_drugs, conditions=None):

    # -----------------------------
    # STEP 1: NORMALIZE INPUT
    # -----------------------------
    drugs = [d.lower().strip() for d in input_drugs]

    final_generics = []
    drug_cards = []

    # -----------------------------
    # STEP 2: DB LOOKUP
    # -----------------------------
    for drug in drugs:

        result = search_drug(drug)

        if result["status"] == "found":
            generic = result["generic_name"]
        else:
            generic = drug  # fallback

        # clean
        generic = generic.lower().strip()

        # -----------------------------
        # STEP 3: HANDLE GENERICS (FIXED)
        # -----------------------------
        primary_generic = generic.split("+")[0].strip().lower()

        if primary_generic:
            final_generics.append(primary_generic)

        # -----------------------------
        # STEP 4: BUILD DRUG CARDS
        # -----------------------------
        drug_cards.append(format_drug(result))

    # -----------------------------
    # STEP 5: REMOVE DUPLICATES
    # -----------------------------
    final_generics = list(set(final_generics))

    print("🔹 BEFORE NORMALIZATION:", final_generics)

    # -----------------------------
    # STEP 6: RXNORM NORMALIZATION
    # -----------------------------
    try:
        norm = normalize_medication_names(final_generics)

        if isinstance(norm, dict) and "normalized" in norm:
            final_generics = norm["normalized"]

    except Exception as e:
        print("❌ Normalization failed:", e)

    print("✅ AFTER NORMALIZATION:", final_generics)

    # -----------------------------
    # STEP 7: DDI CHECK
    # -----------------------------
    try:
        ddi = drug_interaction_check(medications=final_generics)
    except Exception as e:
        print("❌ DDI failed:", e)
        ddi = {"interactions": []}

    # -----------------------------
    # STEP 8: FORMAT DDI OUTPUT
    # -----------------------------
    interactions = []

    for i in ddi.get("interactions", []):
        interactions.append({
            "drug1": i.get("drug_a") or i.get("drug1") or "Unknown",
            "drug2": i.get("drug_b") or i.get("drug2") or "Unknown",
            "severity": (i.get("severity") or "minor").lower(),
            "description": i.get("description", ""),
            "recommendation": i.get("clinical_advice", "Monitor closely")
        })

    print("🔥 INTERACTIONS:", interactions)

    # -----------------------------
    # CLEAN GENERICS (IMPORTANT FIX)
    # -----------------------------
    clean_generics = list(set(final_generics))

    print("🧪 CLEAN GENERICS:", clean_generics)

    # -----------------------------
    # STEP 9: FOOD INTERACTIONS
    # -----------------------------
    food = get_food_interactions(clean_generics)

    # -----------------------------
    # STEP 10: DISEASE INTERACTIONS
    # -----------------------------
    if not conditions:
        conditions = []

    disease = get_disease_interactions(clean_generics, conditions)

    # -----------------------------
    # 🧠 AI SUMMARY
    # -----------------------------
    try:
        doctor_summary = generate_ai_summary(drug_cards, interactions, "doctor")
        patient_summary = generate_ai_summary(drug_cards, interactions, "patient")
    except Exception as e:
        print("❌ AI Summary failed:", e)
        doctor_summary = "Summary not available"
        patient_summary = "Summary not available"

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "drugs": drug_cards,
        "interactions": interactions,
        "food_interactions": food,
        "disease_interactions": disease,
        "summary": {
            "doctor": doctor_summary,
            "patient": patient_summary
        }
    }