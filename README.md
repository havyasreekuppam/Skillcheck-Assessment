# 🚀 SkillCheck – ATS Resume Scorer + Skill Assessment Dashboard

SkillCheck is a web platform that evaluates resumes using ATS (Applicant Tracking System) logic, compares them with Job Descriptions using ML + NLP, and allows users to take Python assessments (Easy / Medium / Hard / Mixed).  
All assessment results are visualized in a **dashboard with progress graphs**.

---

## 🔥 Features

### ✅ RESUME MODULE (Backend + ML)
- Upload resume (PDF / Text)
- Extract content automatically
- Get:
  - ATS score
  - Skill match percentage
  - Missing keywords
- ML models used:
  - `resume_match_model.pkl`
  - `vectorizer.pkl`

---

### 🧠 ASSESSMENT MODULE (Frontend)
- Difficulty levels:
  - ✅ Easy (fixed 50 Q bank → picks 10 random)
  - ✅ Medium (complete Q bank)
  - ✅ Hard (complete Q bank)
  - ✅ Mixed Mode (user decides number of questions + mix of difficulties)
- Auto-calculates score and shows:
  - Pie chart result (Chart.js)
  - Saves attempt history with score + timestamp + difficulty
- Results stored in:
  ```json
  localStorage.assessmentHistory



project structure
Skillcheck-Assessment/
│
├── backend/
│   ├── app.py                  ← Flask main backend
│   ├── ats_backend.py
│   ├── ats_score.py
│   ├── jd_match.py
│   ├── dashboard_api.py
│   ├── utils.py
│   ├── requirements.txt
│   └── data/
│       ├── assessments.json    ← assessment history
│       └── ats_history.json    ← resume score history
│
├── ml_models/
│   ├── ats_score_model.pkl
│   ├── resume_match_model.pkl
│   └── vectorizer.pkl
│
├── assessment_easy.html
├── assessment_medium.html
├── assessment_hard.html
├── assessment_mixed.html
├── dashboard.html
├── main.html
├── login.html
├── signup.html
├── start_assessment.html
├── style.css
└── README.md

1. Create virtual environment

Mac/Linux

python3 -m venv venv
source venv/bin/activate


Windows

python -m venv venv
venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt

3. Run backend
python3 app.py


Backend starts here:

http://127.0.0.1:5000/

4. Run frontend

Just open:

main.html
