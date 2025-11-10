from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------- NVIDIA API KEY ----------------
NVIDIA_API_KEY = "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"

ats_cache = {}

# ------------------------------------------------------------
# ✅ Ensure data folder exists
# ------------------------------------------------------------
if not os.path.exists("data"):
    os.mkdir("data")

ASSESS_DATA_PATH = os.path.join("data", "assessments.json")
ATS_HISTORY_PATH = os.path.join("data", "ats_history.json")


# ✅ Initialize json files if empty
def ensure_json(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, "w") as f:
            json.dump([], f, indent=4)


ensure_json(ASSESS_DATA_PATH)
ensure_json(ATS_HISTORY_PATH)


# --------------------------------------------------------------
# ✅ ROUTE: ATS Resume Score Checker (NVIDIA API)
# --------------------------------------------------------------
@app.route('/api/ats-score', methods=['POST'])
def ats_score_route():
    resume_file = request.files.get("resume")
    job_roles = request.form.getlist("job_roles[]")

    if not resume_file or not job_roles:
        return jsonify({"error": "Missing resume or job role"}), 400

    # Extract text from uploaded PDF
    reader = PdfReader(resume_file)
    resume_text = " ".join(page.extract_text() or "" for page in reader.pages)
    jd_text = " ".join(job_roles)

    cache_key = resume_text.strip().lower() + "|" + jd_text.strip().lower()

    if cache_key in ats_cache:
        print("✅ Returned cached ATS score")
        return jsonify(ats_cache[cache_key])

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {
                "role": "user",
                "content": f"""
Analyze resume vs job description and return ONLY JSON:

Resume: {resume_text}
Job Description: {jd_text}

Return ONLY:
{{
 "score": <0-100>,
 "feedback": "short feedback",
 "matched": ["skill1"],
 "missing": ["skill1"]
}}
"""
            }
        ],
        "temperature": 0
    }

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}"}

    response = requests.post(url, json=payload, headers=headers)

    try:
        ai_output = response.json()["choices"][0]["message"]["content"]
        json_start = ai_output.find("{")
        json_end = ai_output.rfind("}") + 1
        final_json = json.loads(ai_output[json_start:json_end])
    except Exception as e:
        print("❌ Error parsing JSON:", e)
        return jsonify({"error": "Invalid JSON returned"}), 500

    # ✅ Save to cache
    ats_cache[cache_key] = final_json

    # ✅ Save ATS score to ats_history.json
    ensure_json(ATS_HISTORY_PATH)
    with open(ATS_HISTORY_PATH, "r") as f:
        history = json.load(f)

    history.append({
        "score": final_json["score"],
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    with open(ATS_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)

    return jsonify(final_json)


# --------------------------------------------------------------
# ✅ Save Assessment Score
# --------------------------------------------------------------
@app.route('/api/save-assessment', methods=['POST'])
def save_assessment():
    data = request.get_json()
    score = data.get("score")

    ensure_json(ASSESS_DATA_PATH)

    with open(ASSESS_DATA_PATH, "r") as f:
        assessments = json.load(f)

    assessments.append({
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    with open(ASSESS_DATA_PATH, "w") as f:
        json.dump(assessments, f, indent=4)

    return jsonify({"status": "success", "message": "Score saved"})


# --------------------------------------------------------------
# ✅ Dashboard Stats Route
# --------------------------------------------------------------
@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    ensure_json(ASSESS_DATA_PATH)
    ensure_json(ATS_HISTORY_PATH)

    with open(ASSESS_DATA_PATH, "r") as f:
        assessments = json.load(f)

    with open(ATS_HISTORY_PATH, "r") as f:
        ats_history = json.load(f)

    avg_assessment = sum(a["score"] for a in assessments) // len(assessments) if assessments else 0

    return jsonify({
        "latestAssessment": assessments[-1]["score"] if assessments else 0,
        "latestATS": ats_history[-1]["score"] if ats_history else 0,
        "assessmentAvg": avg_assessment,
        "scores": [a["score"] for a in assessments],
        "dates": [a["date"] for a in assessments]
    })


# --------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
