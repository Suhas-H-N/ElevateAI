# ElevateAI — AI-Powered Interview Preparation Platform

A complete Flask web app for students and freshers to prepare for job interviews with AI-style feedback, progress tracking, and a leaderboard.

---

## Features

- **4 Interview Categories**: HR, Technical, Communication, Aptitude
- **3 Difficulty Levels**: Easy / Medium / Hard (shuffled per session)
- **AI-style Feedback Engine**: Keyword detection, STAR method scoring, word count analysis
- **Speech-to-Text**: Speak answers using your microphone (browser native, no API needed)
- **Hints System**: Contextual hints + STAR framework for every question
- **Progress Dashboard**: Line chart, radar skill chart, category averages
- **Daily Streak Tracker**: Motivational streak count
- **Leaderboard**: Top 10 users by average score
- **Company Packs**: Google, Microsoft, Amazon, Meta, Infosys, Wipro themes
- **Full Answer Review**: Accordion Q&A review with per-question feedback
- **Dark Mode**: System-aware + manual toggle
- **Password Strength Meter**: Live checker on signup & password change
- **Confetti**: Fires on a perfect 100% score 🎉

---

## Setup

```bash
# 1. Clone and enter
git clone <repo>
cd ElevateAI

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Open http://127.0.0.1:5000 in your browser.

---

## File Structure

```
ElevateAI/
├── app.py                  # All routes, models, feedback engine, question bank
├── requirements.txt        # Flask + SQLAlchemy only
├── static/
│   └── style.css           # Complete design system (~800 lines)
└── templates/
    ├── base.html           # Navbar, flash, footer, theme toggle
    ├── login.html
    ├── signup.html
    ├── profile_setup.html
    ├── reset_password.html
    ├── dashboard.html      # Charts, leaderboard, history, company packs
    ├── mode.html           # Difficulty selector
    ├── interview.html      # Answer form, timer, speech, hints
    ├── result.html         # Score ring, feedback, confetti
    ├── review.html         # Full Q&A accordion review  ← NEW (was missing)
    ├── 404.html
    └── 500.html
```

---

## Environment Variables (optional)

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | dev key | Flask session secret |
| `DATABASE_URL` | sqlite:///elevate_ai.db | Any SQLAlchemy URL |
| `FLASK_ENV` | development | Set to `production` to disable debug |

---

## What Was Fixed / Upgraded

| Issue | Fix |
|---|---|
| `review/<result_id>` route missing | Added `answer_history()` route + `review.html` |
| `result.html` broken template vars | Fixed `result_id`, `percentage`, `category` passing |
| Heavy unused ML deps (sklearn, shap) | Removed — pure Flask + SQLAlchemy only |
| No speech-to-text | Added Web Speech API (zero cost, browser native) |
| No hint system | Added per-category contextual hints |
| No streak tracking | Added daily streak calculation on User model |
| No daily tips | Added rotating daily tips banner |
| No password strength | Live strength meter on signup + password change |
| No answer history | Full accordion review page |
| No confetti | Canvas confetti on 100% score |
| Dark mode broken | Full CSS variable system, localStorage persistent |
| Radar chart unused | Connected to real per-category averages |
| Company packs — no routes | Mapped to correct category mode pages |
| Leaderboard static | Live from DB, highlights current user |
| requirements.txt bloat | Reduced from 12 packages to 4 |
