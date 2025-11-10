# ✅ backend/ats_score.py (Improved ATS Scoring v6 - FINAL)

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean(text):
    if not text:
        return ""
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

# ✅ Unified skill mapping with synonyms & smart groups
SKILL_GROUPS = {
    "python": ["python"],
    "django": ["django", "rest", "restapi", "rest api", "drf"],
    "sql": ["sql", "mysql", "dbms", "postgres", "sqlite"],
    "git": ["git", "github"],
    "api": ["api", "microservices", "web services"],
    "docker": ["docker"],
    "cloud": ["aws", "azure", "gcp"],
    "java": ["java", "spring", "springboot", "spring boot"],
    "dsa": ["dsa", "data structures", "oops"],
    "linux": ["linux", "unix"]
}

SOFT_SKILLS = [
    "teamwork", "communication", "leadership",
    "problem solving", "collaboration"
]

def find_matching_skills(resume_text):
    matches = []
    for key, words in SKILL_GROUPS.items():
        for w in words:
            if w in resume_text:
                matches.append(key)
                break
    return list(set(matches))

def calculate_ats_score(resume_text, jd_text):
    resume = clean(resume_text)
    jd = clean(jd_text)

    # ✅ Hard skill check (50 pts)
    matched_skills = find_matching_skills(resume)
    hard_score = (len(matched_skills) / len(SKILL_GROUPS)) * 50

    # ✅ JD–Resume matching (25 pts)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume, jd])
    jd_match_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 25

    # ✅ Soft skill matching (15 pts)
    matched_soft = [s for s in SOFT_SKILLS if s in resume]
    soft_score = (len(matched_soft) / len(SOFT_SKILLS)) * 15

    # ✅ Job title matching (5 pts)
    title_score = 5 if "developer" in resume or "engineer" in resume else 2

    # ✅ Education (5 pts)
    education_keywords = ["btech", "b.tech", "bachelor", "degree"]
    education_score = 5 if any(e in resume for e in education_keywords) else 2

    final_score = round(min(100, max(0, hard_score + jd_match_score + soft_score + title_score + education_score)), 2)

    # ✅ Missing skills
    missing = [k for k in SKILL_GROUPS.keys() if k not in matched_skills]

    feedback = (
        "Strong Match ✅ Great for backend roles!"
        if final_score >= 80 else
        "Good Match 👍 Add more backend keywords."
        if final_score >= 60 else
        "Average ⚠ Improve backend projects & experience."
        if final_score >= 40 else
        "Weak Match ❌ Add technical skills & achievements."
    )

    return {
        "score": final_score,
        "matched": matched_skills,
        "missing": missing,
        "feedback": feedback
    }
