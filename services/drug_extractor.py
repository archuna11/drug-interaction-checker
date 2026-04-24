import re
from config import get_db_connection

# 🔥 Words to ignore (very important)
STOPWORDS = {
    "take", "after", "before", "food", "name", "patient",
    "advice", "daily", "morning", "night", "bd", "tid",
    "rx", "tab", "cap"
}


def clean_word(word):
    word = word.strip().lower()
    word = re.sub(r"[^a-z]", "", word)  # keep only letters
    return word


def is_valid_drug(word, cursor):

    # 🔥 check in DB (generic or brand)
    cursor.execute("""
        SELECT 1 FROM drugs_1mg
        WHERE LOWER(drug_name) LIKE ?
        OR LOWER(generic_name) LIKE ?
        LIMIT 1
    """, (f"%{word}%", f"%{word}%"))

    return cursor.fetchone() is not None


def extract_drugs_from_text(text):

    conn = get_db_connection()
    cursor = conn.cursor()

    words = text.split()

    drugs = []

    for w in words:

        w = clean_word(w)

        if len(w) < 4:
            continue

        if w in STOPWORDS:
            continue

        # 🔥 ONLY KEEP VALID DRUGS
        if is_valid_drug(w, cursor):
            drugs.append(w)

    conn.close()

    # remove duplicates
    drugs = list(set(drugs))

    print("🧪 FILTERED DRUGS:", drugs)

    return drugs