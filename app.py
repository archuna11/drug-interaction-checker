from flask import Flask, request, jsonify, render_template
from services.pipeline import run_pipeline
import os
from services.ocr import extract_text
from services.drug_extractor import extract_drugs_from_text

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")




@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    drugs = data.get("drugs", [])

    if not drugs:
        return jsonify({"error": "No drugs provided"}), 400

    result = run_pipeline(drugs)

    return jsonify(result)



# 🔥 CREATE UPLOAD FOLDER
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔥 ADD THIS ROUTE
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 📄 OCR
        text = extract_text(filepath)
        print("📄 OCR TEXT:", text[:200])

        # 💊 Extract drugs
        drugs = extract_drugs_from_text(text)
        print("💊 DETECTED:", drugs)

        # 🔬 Run pipeline
        result = run_pipeline(drugs)

        return jsonify({
            "detected_drugs": drugs,
            "analysis": result
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    

