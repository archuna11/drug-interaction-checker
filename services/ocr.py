import pytesseract
from PIL import Image
import pdfplumber
import re

# 🔥 IMPORTANT (Windows users)
# Uncomment if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(filepath):

    text = ""

    # -----------------------------
    # PDF
    # -----------------------------
    if filepath.lower().endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + " "

    # -----------------------------
    # IMAGE
    # -----------------------------
    else:
        image = Image.open(filepath)
        image = image.convert("L")
        text = pytesseract.image_to_string(image)

    # -----------------------------
    # CLEAN TEXT
    # -----------------------------
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text