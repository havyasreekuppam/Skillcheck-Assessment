from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)  # ✅ allows your HTML (localhost) to talk to Flask backend

model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/api/ats-score', methods=['POST'])
def ats_score():
    data = request.get_json()
    resume_text = data.get("resume", "")
    job_desc = data.get("job_desc", "")

    if not resume_text or not job_desc:
        return jsonify({"error": "Missing resume or job description"}), 400

    embeddings = model.encode([resume_text, job_desc], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    score_percent = round(score * 100, 2)

    feedback = (
        "Excellent match! ✅" if score_percent >= 80 else
        "Good match 👍" if score_percent >= 60 else
        "Needs improvement 🚀" if score_percent >= 40 else
        "Weak match ❌"
    )

    return jsonify({
        "score": score_percent,
        "feedback": feedback
    })

if __name__ == '__main__':
    app.run(debug=True)
