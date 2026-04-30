import re
from config import get_db_connection

# 🔥 Words to ignore
STOPWORDS = {
    "take", "after", "before", "food", "name", "patient",
    "advice", "daily", "morning", "night", "bd", "tid",
    "rx", "tab", "cap", "male", "female", "type", "once",
    "pain", "salt", "year", "old"
}


def clean_word(word):
    word = word.strip().lower()
    word = re.sub(r"[^a-z]", "", word)
    return word


# ✅ STRICT MATCH (NO LIKE %word%)
def is_valid_drug(word, cursor):
    cursor.execute("""
        SELECT 1 FROM drugs_1mg
        WHERE LOWER(drug_name) = ?
        OR LOWER(generic_name) = ?
        LIMIT 1
    """, (word, word))

    return cursor.fetchone() is not None


def extract_drugs_from_text(text):

    conn = get_db_connection()
    cursor = conn.cursor()

    words = text.split()
    drugs = set()  # 🔥 no duplicates automatically

    for w in words:

        w = clean_word(w)

        if len(w) < 4:
            continue

        if w in STOPWORDS:
            continue

        # 🔥 ONLY STRICT VALID DRUGS
        if is_valid_drug(w, cursor):
            drugs.add(w)

    conn.close()

    drugs = list(drugs)

    print("🧪 FINAL DRUGS:", drugs)

    return drugs