# ElevateAI v2.0 — AI-Powered Interview Preparation Platform

> Final Year Project | Flask · SQLAlchemy · Gemini AI · Chart.js

---

## 🚀 What Is ElevateAI?

ElevateAI is a full-stack web application that helps students and freshers prepare for job interviews through structured practice, AI-powered feedback, and real-time performance analytics.

---

## ✅ Full Feature List

| Feature | Details |
|---------|---------|
| 🤖 **Gemini AI Feedback** | Semantic answer evaluation via Google Gemini 2.0 Flash — scores 0–10, detects keywords, suggests improvements |
| 🎤 **Speech-to-Text** | Browser-native Web Speech API — speak your answers instead of typing |
| 🔥 **Streak Tracker** | Daily practice streaks with banner on dashboard |
| 🎯 **Radar Chart** | Spider chart showing HR / Technical / Communication strengths |
| 📈 **Line Chart** | Score % over time via Chart.js |
| 🏆 **Leaderboard** | Weekly + all-time top scorers (own page + dashboard preview) |
| 📖 **Answer History** | Review every past Q&A with AI feedback, keyword tags, score bars |
| ⏱ **Countdown Timer** | Per-question time limit (Easy 2min / Medium 3min / Hard 4min) — auto-submits |
| 🏢 **Company Packs** | Amazon, Google, TCS, Infosys, Microsoft question sets |
| 💡 **Hint System** | STAR / CAR framework hints shown on demand per category |
| ✉️ **Email Verification** | Flask-Mail + Gmail SMTP — token verified on signup |
| 🔑 **Forgot Password** | Token-based secure reset via email (1-hour expiry) |
| 📄 **Resume Upload** | PDF upload (max 5MB) stored per user |
| 🌙 **Dark / Light Mode** | Persisted in localStorage |
| 🏅 **Difficulty Levels** | Easy / Medium / Hard — different questions AND scoring thresholds |
| 🔐 **Auth** | Hashed passwords (Werkzeug), session management, login guard |
| 🌐 **REST API** | `/api/stats`, `/api/leaderboard`, `/api/hint/<category>` |
| 🐳 **Docker Ready** | `.env.example` + `.gitignore` provided |
| 📱 **Responsive** | Mobile-first layouts for all pages |

---

## 🗂 Project Structure

```
ElevateAI/
├── app.py                        # All Flask routes, models, AI logic
├── requirements.txt
├── .env.example                  # Copy to .env and fill values
├── .gitignore
├── README.md
├── instance/
│   └── elevate_ai.db             # SQLite database (auto-created, git-ignored)
├── static/
│   ├── style.css                 # Complete design system
│   └── uploads/                  # Resume PDFs (git-ignored)
└── templates/
    ├── base.html                 # Navbar, flash, footer, theme toggle
    ├── login.html
    ├── signup.html               # Password strength meter + confirm field
    ├── forgot_password.html
    ├── reset_password.html
    ├── profile_setup.html        # Resume upload + radio pills
    ├── dashboard.html            # Stats, radar, line chart, leaderboard, streaks
    ├── mode.html                 # Difficulty + company pack selection
    ├── interview.html            # Speech-to-text, countdown timer, hint box
    ├── result.html               # AI feedback, keyword tags, confetti on 100%
    ├── history.html              # Past Q&A review with AI scores
    ├── leaderboard.html          # Weekly + all-time tabs
    ├── 404.html
    └── 500.html
```

---

## ⚙️ Setup & Run (Step by Step)

### 1. Clone / Unzip the Project

```bash
# If you downloaded the zip:
unzip ElevateAI_V2.zip
cd ElevateAI_V2

# OR if using git:
git clone https://github.com/YOUR_USERNAME/ElevateAI.git
cd ElevateAI
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `flask-sqlalchemy` | ORM / database layer |
| `flask-mail` | Email sending (Gmail SMTP) |
| `werkzeug` | Password hashing, file uploads |
| `itsdangerous` | Secure tokens (email verify / password reset) |
| `google-genai` | Google Gemini AI feedback |

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
SECRET_KEY=any_long_random_string_here
FLASK_ENV=development

# Gemini AI (free tier — get key from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy...your_key_here

# Gmail SMTP (optional — needed for email verification / forgot password)
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your_16_char_app_password
```

> **To run WITHOUT email / AI:** Leave `GEMINI_API_KEY` and `MAIL_*` blank.
> The app falls back to rule-based feedback and skips email sending.

### 5. Load Environment Variables

```bash
# macOS / Linux
export $(cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v) }
```

### 6. Run the App

```bash
python app.py
```

Open: **http://127.0.0.1:5000**

---

## 📦 Installing google-genai (Gemini AI)

The new SDK replaces the deprecated `google-generativeai`:

```bash
pip install google-genai
```

Get your **free** API key: https://aistudio.google.com/app/apikey

The free tier gives **15 requests/minute** and **1 million tokens/day** — more than enough for a student project.

---

## 📧 Setting Up Gmail for Email Features

1. Go to your Google Account → **Security** → Enable **2-Step Verification**
2. Go to **App Passwords** → Generate a password for "Mail"
3. Copy the 16-character password into `MAIL_PASSWORD` in `.env`

> If you skip this, signup still works — email verification is silently skipped.

---

## 🗄 Database Notes

- SQLite database is auto-created at `instance/elevate_ai.db` on first run
- To reset the database: delete `instance/elevate_ai.db` and restart
- For production, switch to PostgreSQL by setting `DATABASE_URL=postgresql://...` in `.env`

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/stats` | Your total, best, avg score, streak | ✅ Required |
| GET | `/api/leaderboard` | Top 10 users this week | ✅ Required |
| GET | `/api/hint/<category>` | Hint framework for a category | ✅ Required |

Example response for `/api/stats`:
```json
{
  "total": 12,
  "best": 100.0,
  "avg": 83.3,
  "streak": 5
}