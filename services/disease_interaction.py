import json

def get_disease_interactions(drugs, conditions):

    with open("services/data/drug_disease.json") as f:
        rules = json.load(f)

    results = []

    drugs = [d.lower() for d in drugs]
    conditions = [c.lower() for c in conditions]

    for drug in drugs:
        if drug in rules:
            for condition in conditions:
                if condition in rules[drug]:
                    r = rules[drug][condition]

                    results.append({
                        "drug": drug,
                        "condition": condition,
                        "severity": r["severity"],
                        "description": r["description"],
                        "recommendation": r["recommendation"]
                    })

    return results