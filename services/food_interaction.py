
import json
import os

# Load JSON once
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "drug_food.json")

with open(DATA_PATH, "r") as f:
    RULES = json.load(f)


def get_food_interactions(drugs):

    results = []

    # normalize input
    drugs = [d.lower().strip() for d in drugs]

    # 🔥 LOOP ONLY USER DRUGS
    for drug in drugs:

        if drug in RULES:
            r = RULES[drug]

            results.append({
                "drug": drug,
                "severity": r.get("severity", "minor"),
                "description": r.get("description", ""),
                "recommendation": r.get("recommendation", "")
            })

    return results