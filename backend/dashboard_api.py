# backend/dashboard_api.py
from flask import Flask, jsonify
from flask_cors import CORS
import os, json
from datetime import datetime
import numpy as np

# sklearn imports
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
CORS(app)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "assessments.json")

def load_assessments():
    if not os.path.exists(DATA_PATH):
        # return sample generated data if file missing
        return sample_assessments()
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def sample_assessments():
    # sample topics: Variables, OOP, Data Structures, Algorithms, Libraries
    base_date = datetime.now()
    topics = ["Variables", "OOP", "DSA", "Libraries", "Testing"]
    arr = []
    for i in range(8):
        d = (base_date).strftime("%Y-%m-%d")
        # generate slightly improving scores
        topic_scores = {t: max(30, min(100, int(50 + i*4 + np.random.randint(-8, 8)))) for t in topics}
        overall = round(np.mean(list(topic_scores.values())), 2)
        arr.append({
            "id": i+1,
            "date": (base_date).strftime("%Y-%m-%d"),
            "score": overall,
            "topic_scores": topic_scores
        })
    return arr

@app.route("/api/dashboard-stats", methods=["GET"])
def dashboard_stats():
    assessments = load_assessments()
    if not assessments:
        return jsonify({"error":"no data"}), 400

    # Sort by date if possible (if date strings present)
    try:
        assessments_sorted = sorted(assessments, key=lambda x: datetime.fromisoformat(x['date']))
    except Exception:
        assessments_sorted = assessments

    history = [{"date": a["date"], "score": float(a["score"])} for a in assessments_sorted]

    # Trend: linear regression on indices vs score
    X = np.arange(len(history)).reshape(-1,1)
    y = np.array([h["score"] for h in history])
    lr = LinearRegression().fit(X, y)
    slope = float(lr.coef_[0])
    intercept = float(lr.intercept_)
    trend_fit = (lr.predict(X)).tolist()

    trend_text = "Stable"
    if slope > 0.1:
        trend_text = "Improving"
    elif slope < -0.1:
        trend_text = "Declining"

    # Gather topic list and compute per-topic averages
    all_topics = set()
    for a in assessments_sorted:
        all_topics.update(a["topic_scores"].keys())
    all_topics = sorted(list(all_topics))
    topic_matrix = []
    for a in assessments_sorted:
        row = [float(a["topic_scores"].get(t, 0)) for t in all_topics]
        topic_matrix.append(row)
    topic_matrix = np.array(topic_matrix)

    topic_averages = (np.mean(topic_matrix, axis=0)).round(2).tolist()

    # Top strengths and weaknesses
    topic_with_avg = list(zip(all_topics, topic_averages))
    topic_with_avg_sorted = sorted(topic_with_avg, key=lambda x: x[1], reverse=True)
    top_strengths = [t for t,_ in topic_with_avg_sorted[:3]]
    weaknesses = [t for t,_ in topic_with_avg_sorted[-3:]]

    # Clustering attempts (KMeans on topic_matrix)
    n_clusters = min(3, max(1, len(assessments_sorted)//2))
    try:
        if len(assessments_sorted) >= n_clusters and topic_matrix.shape[0] >= n_clusters:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(topic_matrix)
            labels = kmeans.labels_
        else:
            labels = np.zeros(len(assessments_sorted), dtype=int)
    except Exception:
        labels = np.zeros(len(assessments_sorted), dtype=int)

    unique, counts = np.unique(labels, return_counts=True)
    cluster_counts = {f"Cluster {int(k)+1}": int(v) for k,v in zip(unique, counts)}

    # PCA reduce topics to 2 dims for optional plotting (not used directly here)
    try:
        pca = PCA(n_components=min(2, topic_matrix.shape[1]))
        pca_coords = pca.fit_transform(topic_matrix).tolist()
    except Exception:
        pca_coords = []

    result = {
        "history": history,
        "trend_fit": [float(x) for x in trend_fit],
        "trend_slope": round(slope, 6),
        "trend_text": trend_text,
        "overall_average": round(float(np.mean([h["score"] for h in history])), 2),
        "topics": {
            "labels": all_topics,
            "values": topic_averages
        },
        "top_strengths": top_strengths,
        "weaknesses": weaknesses,
        "clusters": {
            "counts": cluster_counts,
            "labels": labels.tolist()
        },
        "pca_coords": pca_coords,
        "raw_assessments_count": len(assessments_sorted)
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
