"""
ElevateAI - AI-Powered Interview Preparation Platform
Fully Complete Production Build — Flask + SQLite
"""

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
from collections import defaultdict
import os, re, json, random

app = Flask(__name__)

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "elevate_ai_dev_secret_2026_change_in_prod")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///elevate_ai.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

db = SQLAlchemy(app)


# ──────────────────────────────────────────────
# DECORATORS
# ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ──────────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(30))
    college = db.Column(db.String(200))
    degree = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    year_of_study = db.Column(db.String(50))
    profession = db.Column(db.String(100))
    profile_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship("InterviewResult", backref="user", lazy=True)

    @property
    def streak(self):
        """Calculate current daily streak."""
        if not self.results:
            return 0
        dates = sorted(set(r.date.date() for r in self.results), reverse=True)
        if not dates:
            return 0
        today = date.today()
        if dates[0] < today - timedelta(days=1):
            return 0
        streak = 1
        for i in range(1, len(dates)):
            if dates[i-1] - dates[i] == timedelta(days=1):
                streak += 1
            else:
                break
        return streak

    @property
    def total_attempts(self):
        return len(self.results)

    @property
    def best_score(self):
        return round(max((r.percentage for r in self.results), default=0), 1)

    @property
    def avg_score(self):
        if not self.results:
            return 0
        return round(sum(r.percentage for r in self.results) / len(self.results), 1)


class InterviewResult(db.Model):
    __tablename__ = "interview_results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default="medium")
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    answers_json = db.Column(db.Text, default="[]")   # JSON-encoded answers list
    feedback_json = db.Column(db.Text, default="[]")  # JSON-encoded feedback list
    questions_json = db.Column(db.Text, default="[]") # JSON-encoded questions list
    date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def answers(self):
        try:
            return json.loads(self.answers_json or "[]")
        except Exception:
            return []

    @property
    def feedback(self):
        try:
            return json.loads(self.feedback_json or "[]")
        except Exception:
            return []

    @property
    def questions(self):
        try:
            return json.loads(self.questions_json or "[]")
        except Exception:
            return []


# ──────────────────────────────────────────────
# QUESTION BANK (Difficulty-Aware + Expanded)
# ──────────────────────────────────────────────
QUESTION_BANK = {
    "hr": {
        "easy": [
            "Tell me about yourself.",
            "What are your hobbies and interests?",
            "Why did you choose your field of study?",
            "Describe yourself in three words.",
            "What are you passionate about outside of work?",
        ],
        "medium": [
            "Why should we hire you over other candidates?",
            "What are your greatest strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Describe a time you worked successfully in a team.",
            "How do you handle competing priorities at work?",
        ],
        "hard": [
            "Tell me about a time you failed and what you learned from it.",
            "How do you handle conflict with a teammate or supervisor?",
            "Describe a situation where you had to adapt quickly to change.",
            "What's your strategy for managing multiple competing priorities under pressure?",
            "Tell me about a time you took initiative without being asked.",
        ],
    },
    "technical": {
        "easy": [
            "What is Object-Oriented Programming and name its four pillars?",
            "Explain the difference between a list and a tuple in Python.",
            "What is a database and why is it used?",
            "What is an API and give an example of how it's used.",
            "What is the difference between compiled and interpreted languages?",
        ],
        "medium": [
            "Explain the difference between SQL and NoSQL databases.",
            "What is the MVC design pattern and where is it used?",
            "Explain time complexity and give an example of O(n log n).",
            "What is the difference between authentication and authorization?",
            "Explain RESTful APIs and their key principles.",
        ],
        "hard": [
            "Explain CAP theorem and how it applies to distributed systems.",
            "How does a hash table work internally, and what causes collisions?",
            "Describe the microservices architecture and its trade-offs vs. monoliths.",
            "How would you design a URL shortening service like bit.ly?",
            "Explain SOLID principles and give a real-world example of each.",
        ],
    },
    "communication": {
        "easy": [
            "Describe your favorite project in simple terms.",
            "How do you explain a technical topic to a non-technical person?",
            "Tell me about a time you helped a friend or colleague.",
            "What motivates you to do your best work?",
            "How do you introduce yourself in a professional setting?",
        ],
        "medium": [
            "How do you handle pressure and tight deadlines?",
            "Describe a situation where you had to deliver difficult news.",
            "How do you give and receive constructive feedback?",
            "Describe your communication style when working in a diverse team.",
            "How do you ensure your message is understood correctly?",
        ],
        "hard": [
            "Describe a situation where your communication prevented a major mistake.",
            "How would you resolve a misunderstanding between two departments?",
            "Tell me about a time you had to persuade stakeholders to change direction.",
            "How do you ensure clarity when communicating complex decisions remotely?",
            "Describe how you'd present a failed project to leadership honestly.",
        ],
    },
    "aptitude": {
        "easy": [
            "A train travels 60 km/h for 2 hours. How far does it travel?",
            "If 5 workers complete a job in 10 days, how many days for 10 workers?",
            "What is 15% of 200?",
            "If a product costs ₹800 after a 20% discount, what was the original price?",
            "Find the next number in the series: 2, 4, 8, 16, __",
        ],
        "medium": [
            "A can do a piece of work in 12 days, B in 15 days. How many days together?",
            "If the ratio of A to B is 3:5 and B to C is 2:3, what is A:B:C?",
            "A pipe fills a tank in 6 hours. Another empties it in 10 hours. Time to fill with both?",
            "A man invests ₹10,000 at 10% compound interest for 2 years. Final amount?",
            "If APPLE = 50 in some code, what is MANGO?",
        ],
        "hard": [
            "Two trains 200m and 150m long approach each other at 60 and 90 km/h. Time to cross?",
            "In a 500 m race, A beats B by 50 m and B beats C by 25 m. By how much does A beat C?",
            "A cistern has a leak at the bottom. A pipe fills it in 8 hours; with leak, 10 hours. Time for leak alone?",
            "A sum becomes ₹26,010 in 3 years and ₹30,012 in 4 years at simple interest. Find the principal.",
            "There are 20 people in a room. Every person shakes hands with every other person exactly once. How many handshakes?",
        ],
    },
}

APTITUDE_ANSWERS = {
    "aptitude": {
        "easy": [
            "120 km. Distance = Speed × Time = 60 × 2.",
            "5 days. More workers = less time. (5 × 10) / 10 = 5.",
            "30. 15/100 × 200 = 30.",
            "₹1,000. 800 = 80% of original. Original = 800/0.8 = 1000.",
            "32. Each number doubles: 2, 4, 8, 16, 32.",
        ],
        "medium": [
            "6⅔ days. Combined rate = 1/12 + 1/15 = 9/60 = 3/20. Days = 20/3.",
            "6:10:15. A:B = 3:5, B:C = 2:3 → scale B to 10 → A:B:C = 6:10:15.",
            "15 hours. Net fill rate = 1/6 - 1/10 = 4/60 = 1/15.",
            "₹12,100. 10000 × (1.1)² = 12,100.",
            "Depends on the code pattern given. State your logic clearly.",
        ],
        "hard": [
            "~10.8 seconds. Relative speed = 150 km/h = 41.67 m/s. Total length = 350m. Time = 350/41.67.",
            "~73.75 m. A beats C by 50 + 25 - (50×25/500) = 72.5 m approx.",
            "40 hours. Leak rate = 1/8 - 1/10 = 2/80 = 1/40.",
            "₹18,000. Difference in amounts = SI for 1 year = ₹4002. For 3 years = ₹12,006. Principal = 26010 - 12006.",
            "190 handshakes. Formula: n(n-1)/2 = 20×19/2 = 190.",
        ],
    }
}

CATEGORY_META = {
    "hr":            {"icon": "👔", "label": "HR Round",      "color": "#6366F1", "description": "Behavioral & personality questions"},
    "technical":     {"icon": "⚙️",  "label": "Technical",     "color": "#0EA5E9", "description": "Core CS & engineering concepts"},
    "communication": {"icon": "💬", "label": "Communication", "color": "#10B981", "description": "Soft skills & situational questions"},
    "aptitude":      {"icon": "🧠", "label": "Aptitude",      "color": "#F59E0B", "description": "Logical reasoning & problem solving"},
}

DIFFICULTY_META = {
    "easy":   {"label": "Easy",   "color": "#22C55E", "icon": "🟢"},
    "medium": {"label": "Medium", "color": "#F59E0B", "icon": "🟡"},
    "hard":   {"label": "Hard",   "color": "#EF4444", "icon": "🔴"},
}

INTERVIEW_TIPS = {
    "hr": [
        "Use the STAR method: Situation → Task → Action → Result",
        "Be authentic — interviewers detect rehearsed answers quickly",
        "Always quantify your impact when possible (e.g., improved efficiency by 30%)",
        "Research the company's values and align your answers to them",
    ],
    "technical": [
        "Think out loud — interviewers want to see your problem-solving process",
        "It's okay to ask clarifying questions before answering",
        "Mention trade-offs and alternatives, not just one solution",
        "Relate abstract concepts to real-world examples",
    ],
    "communication": [
        "Keep answers concise — 2 minutes max per answer is ideal",
        "Structure your answer: context → challenge → action → outcome",
        "Show empathy and emotional intelligence in situational answers",
        "Use specific examples, not generic statements like 'I always communicate well'",
    ],
    "aptitude": [
        "Show your working clearly — partial credit matters",
        "Estimate first, then calculate — shows numerical sense",
        "Check your answer by working backwards",
        "Identify the pattern or formula before diving in",
    ],
}

COMPANY_PACKS = [
    {"icon": "🏢", "name": "Google",    "desc": "System design + coding",  "category": "technical"},
    {"icon": "💻", "name": "Microsoft", "desc": "Behavioral + technical",   "category": "hr"},
    {"icon": "📦", "name": "Amazon",    "desc": "Leadership principles",    "category": "hr"},
    {"icon": "🔵", "name": "Meta",      "desc": "Communication focus",      "category": "communication"},
    {"icon": "🚀", "name": "Infosys",   "desc": "Aptitude + HR mix",        "category": "aptitude"},
    {"icon": "🟠", "name": "Wipro",     "desc": "Logical reasoning focus",  "category": "aptitude"},
]


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)


def is_strong_password(password):
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
    )


def generate_feedback(answers, difficulty="medium", category="hr"):
    """
    Enhanced rule-based feedback engine with keyword analysis and STAR detection.
    """
    thresholds = {"easy": 10, "medium": 20, "hard": 35}
    min_words = thresholds.get(difficulty, 20)

    # Category-specific power keywords to detect
    KEYWORDS = {
        "hr": ["team", "led", "managed", "improved", "achieved", "result", "learned", "challenge", "initiative", "collaborate", "success", "impact", "responsibility"],
        "technical": ["algorithm", "complexity", "database", "api", "architecture", "pattern", "scalable", "optimize", "deploy", "test", "system", "design", "performance"],
        "communication": ["communicated", "clarified", "presented", "resolved", "explained", "listened", "stakeholder", "feedback", "aligned", "understood", "transparent"],
        "aptitude": ["calculate", "formula", "ratio", "rate", "percentage", "distance", "time", "probability", "series", "logic", "work", "speed"],
    }
    STAR_WORDS = ["situation", "task", "action", "result", "outcome", "achieved", "led", "then", "finally", "ultimately"]

    cat_keywords = KEYWORDS.get(category, KEYWORDS["hr"])
    feedback = []

    for ans in answers:
        ans_stripped = ans.strip()
        word_list = ans_stripped.lower().split() if ans_stripped else []
        word_count = len(word_list)

        keywords_hit = [kw for kw in cat_keywords if kw in word_list]
        has_star = sum(1 for sw in STAR_WORDS if sw in word_list) >= 2

        if word_count == 0:
            feedback.append({
                "rating": "skipped", "icon": "⚠️",
                "text": "No answer provided. Always attempt every question — partial credit is better than none.",
                "keywords_hit": [], "missing_aspects": ["answer", "example", "detail"],
            })
        elif word_count < 5:
            feedback.append({
                "rating": "poor", "icon": "❌",
                "text": f"Answer too brief ({word_count} words). Use the STAR method: Situation, Task, Action, Result. Give concrete details.",
                "keywords_hit": keywords_hit, "missing_aspects": [k for k in cat_keywords[:3] if k not in word_list],
            })
        elif word_count < min_words:
            feedback.append({
                "rating": "fair", "icon": "⚡",
                "text": f"Decent attempt ({word_count} words), but needs more depth. Add a specific example and a measurable outcome.",
                "keywords_hit": keywords_hit, "missing_aspects": [k for k in cat_keywords[:3] if k not in word_list],
            })
        elif word_count < min_words * 2:
            star_note = " Good use of the STAR structure!" if has_star else " Try adding a clear outcome to strengthen it."
            feedback.append({
                "rating": "good", "icon": "✅",
                "text": f"Good answer ({word_count} words). Clear and structured.{star_note}",
                "keywords_hit": keywords_hit, "missing_aspects": [],
            })
        else:
            star_note = " Excellent STAR structure detected!" if has_star else ""
            feedback.append({
                "rating": "excellent", "icon": "🌟",
                "text": f"Excellent response ({word_count} words). Comprehensive, detailed, and well-articulated.{star_note}",
                "keywords_hit": keywords_hit, "missing_aspects": [],
            })

    return feedback


def get_performance_label(percentage):
    if percentage == 100:
        return {"label": "Perfect Score!", "icon": "🏆", "cls": "perfect"}
    elif percentage >= 75:
        return {"label": "Outstanding",    "icon": "🌟", "cls": "excellent"}
    elif percentage >= 50:
        return {"label": "Good Progress",  "icon": "👍", "cls": "good"}
    elif percentage >= 25:
        return {"label": "Keep Practicing","icon": "⚡", "cls": "fair"}
    else:
        return {"label": "Needs Improvement","icon": "💪","cls": "improve"}


def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


def get_leaderboard():
    """Return top 10 users by average score with at least 1 attempt."""
    users = User.query.all()
    lb = []
    for u in users:
        if u.results:
            avg = round(sum(r.percentage for r in u.results) / len(u.results), 1)
            lb.append({
                "username": u.username,
                "name": u.name or u.username,
                "avg": avg,
                "attempts": len(u.results),
                "best": round(max(r.percentage for r in u.results), 1),
            })
    lb.sort(key=lambda x: (-x["avg"], -x["attempts"]))
    return lb[:10]


# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Both fields are required.", "warning")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.name or user.username}! 👋", "success")
            return redirect(url_for("profile_setup") if not user.profile_complete else url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm_password", "").strip()
        errors   = []

        if not username or not email or not password:
            errors.append("All fields are required.")
        elif len(username) < 3 or len(username) > 30:
            errors.append("Username must be 3–30 characters.")
        elif not re.match(r"^[a-z0-9_]+$", username):
            errors.append("Username: only lowercase letters, numbers, underscores.")
        elif not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        elif not is_strong_password(password):
            errors.append("Password must be ≥ 8 characters with 1 uppercase & 1 number.")
        elif password != confirm:
            errors.append("Passwords do not match.")
        elif User.query.filter_by(username=username).first():
            errors.append("Username is already taken.")
        elif User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return redirect(url_for("signup"))

        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You've been signed out. See you soon! 👋", "info")
    return redirect(url_for("login"))


@app.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    user = get_current_user()
    if request.method == "POST":
        old_pwd = request.form.get("old_password", "").strip()
        new_pwd = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not check_password_hash(user.password, old_pwd):
            flash("Current password is incorrect.", "danger")
        elif not is_strong_password(new_pwd):
            flash("New password must be ≥ 8 chars with 1 uppercase & 1 number.", "warning")
        elif new_pwd != confirm:
            flash("Passwords do not match.", "warning")
        else:
            user.password = generate_password_hash(new_pwd)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("dashboard"))

    return render_template("reset_password.html", user=user)


# ──────────────────────────────────────────────
# PROFILE ROUTES
# ──────────────────────────────────────────────
@app.route("/profile_setup", methods=["GET", "POST"])
@login_required
def profile_setup():
    user = get_current_user()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name:
            flash("Full name is required.", "warning")
            return redirect(url_for("profile_setup"))

        if email and email != user.email:
            if not is_valid_email(email):
                flash("Invalid email address.", "warning")
                return redirect(url_for("profile_setup"))
            if User.query.filter(User.email == email, User.id != user.id).first():
                flash("That email is already in use.", "danger")
                return redirect(url_for("profile_setup"))
            user.email = email

        user.name = name
        dob_raw = request.form.get("dob", "")
        if dob_raw:
            try:
                user.dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
            except ValueError:
                pass

        user.gender       = request.form.get("gender", "")
        user.college      = request.form.get("college", "").strip()
        user.degree       = request.form.get("degree", "").strip()
        user.branch       = request.form.get("branch", "").strip()
        user.year_of_study = request.form.get("year_of_study", "")
        user.profession   = request.form.get("profession", "")
        user.profile_complete = True

        db.session.commit()
        flash("Profile saved successfully! ✨", "success")
        return redirect(url_for("dashboard"))

    return render_template("profile_setup.html", user=user)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    results = (
        InterviewResult.query
        .filter_by(user_id=user.id)
        .order_by(InterviewResult.date.asc())
        .all()
    )

    # Chart data (last 15 entries)
    chart_results = results[-15:]
    chart_labels = [r.date.strftime("%d %b") for r in chart_results]
    chart_scores = [r.percentage for r in chart_results]
    chart_cats   = [r.category for r in chart_results]

    # Category breakdown
    cat_stats = defaultdict(lambda: {"total": 0, "attempts": 0})
    for r in results:
        cat_stats[r.category]["total"] += r.percentage
        cat_stats[r.category]["attempts"] += 1

    category_averages = {
        cat: round(v["total"] / v["attempts"], 1)
        for cat, v in cat_stats.items()
    }

    # Radar chart data (avg per category)
    radar_labels = [CATEGORY_META[c]["label"] for c in CATEGORY_META]
    radar_scores = [category_averages.get(c, 0) for c in CATEGORY_META]

    # Leaderboard
    leaderboard = get_leaderboard()
    current_username = user.username

    # Random daily tip
    tip_category = list(INTERVIEW_TIPS.keys())[datetime.now().day % 4]
    daily_tip = random.choice(INTERVIEW_TIPS[tip_category])

    return render_template(
        "dashboard.html",
        user=user,
        results=results,
        total_attempts=user.total_attempts,
        best_score=user.best_score,
        avg_score=user.avg_score,
        streak=user.streak,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
        chart_cats=chart_cats,
        category_averages=category_averages,
        category_meta=CATEGORY_META,
        difficulty_meta=DIFFICULTY_META,
        radar_labels=radar_labels,
        radar_scores=radar_scores,
        leaderboard=leaderboard,
        current_username=current_username,
        company_packs=COMPANY_PACKS,
        daily_tip=daily_tip,
        tip_category=tip_category,
    )


# ──────────────────────────────────────────────
# INTERVIEW FLOW
# ──────────────────────────────────────────────
@app.route("/mode")
@login_required
def mode():
    category = request.args.get("category", "")
    if category not in QUESTION_BANK:
        flash("Invalid interview category.", "danger")
        return redirect(url_for("dashboard"))
    return render_template(
        "mode.html",
        category=category,
        meta=CATEGORY_META[category],
        difficulty_meta=DIFFICULTY_META,
        tips=INTERVIEW_TIPS.get(category, []),
    )


@app.route("/interview", methods=["GET", "POST"])
@login_required
def interview():
    category   = request.args.get("category", session.get("interview_category"))
    difficulty = request.args.get("difficulty", session.get("interview_difficulty", "medium"))

    # Initialize new session on fresh start
    if category and request.method == "GET" and request.args.get("category"):
        if category not in QUESTION_BANK or difficulty not in QUESTION_BANK.get(category, {}):
            flash("Invalid interview configuration.", "danger")
            return redirect(url_for("dashboard"))

        # Shuffle questions for variety
        qs = QUESTION_BANK[category][difficulty][:]
        random.shuffle(qs)

        session["interview_category"]  = category
        session["interview_difficulty"] = difficulty
        session["interview_q_index"]   = 0
        session["interview_answers"]   = []
        session["interview_questions"] = qs

    if "interview_category" not in session:
        return redirect(url_for("dashboard"))

    cat       = session["interview_category"]
    diff      = session["interview_difficulty"]
    questions = session.get("interview_questions", QUESTION_BANK[cat][diff])

    if request.method == "POST":
        answer  = request.form.get("answer", "").strip()
        answers = session.get("interview_answers", [])
        answers.append(answer)
        session["interview_answers"] = answers
        session["interview_q_index"] = session.get("interview_q_index", 0) + 1

    q_index = session.get("interview_q_index", 0)

    # Interview complete → generate results
    if q_index >= len(questions):
        answers       = session.get("interview_answers", [])
        feedback_list = generate_feedback(answers, diff, cat)

        score      = sum(1 for f in feedback_list if f["rating"] in ("good", "excellent"))
        total      = len(questions)
        percentage = round((score / total) * 100, 1) if total > 0 else 0

        user = get_current_user()
        result = InterviewResult(
            user_id       = user.id,
            category      = cat,
            difficulty    = diff,
            score         = score,
            total         = total,
            percentage    = percentage,
            answers_json  = json.dumps(answers),
            feedback_json = json.dumps(feedback_list),
            questions_json= json.dumps(questions),
        )
        db.session.add(result)
        db.session.commit()

        for key in ["interview_category", "interview_difficulty", "interview_q_index",
                    "interview_answers", "interview_questions"]:
            session.pop(key, None)

        performance      = get_performance_label(percentage)
        feedback_with_qa = list(zip(feedback_list, questions, answers))
        tips             = INTERVIEW_TIPS.get(cat, [])

        return render_template(
            "result.html",
            result_id       = result.id,
            score           = score,
            total           = total,
            percentage      = percentage,
            category        = cat,
            difficulty      = diff,
            feedback_with_qa= feedback_with_qa,
            performance     = performance,
            meta            = CATEGORY_META[cat],
            difficulty_meta = DIFFICULTY_META[diff],
            tips            = tips,
        )

    question = questions[q_index]
    tips     = INTERVIEW_TIPS.get(cat, [])

    # Aptitude: pass expected answer for reference
    apt_answer = None
    if cat == "aptitude":
        try:
            apt_answer = APTITUDE_ANSWERS["aptitude"][diff][q_index]
        except (KeyError, IndexError):
            apt_answer = None

    return render_template(
        "interview.html",
        question        = question,
        current         = q_index + 1,
        total           = len(questions),
        category        = cat,
        difficulty      = diff,
        meta            = CATEGORY_META[cat],
        difficulty_meta = DIFFICULTY_META[diff],
        progress        = round((q_index / len(questions)) * 100),
        tips            = tips,
        apt_answer      = apt_answer,
    )


# ──────────────────────────────────────────────
# ANSWER HISTORY / REVIEW
# ──────────────────────────────────────────────
@app.route("/review/<int:result_id>")
@login_required
def answer_history(result_id):
    user   = get_current_user()
    result = InterviewResult.query.filter_by(id=result_id, user_id=user.id).first_or_404()

    feedback_with_qa = list(zip(result.feedback, result.questions, result.answers))
    performance      = get_performance_label(result.percentage)

    return render_template(
        "review.html",
        result          = result,
        feedback_with_qa= feedback_with_qa,
        performance     = performance,
        meta            = CATEGORY_META.get(result.category, CATEGORY_META["hr"]),
        difficulty_meta = DIFFICULTY_META.get(result.difficulty, DIFFICULTY_META["medium"]),
        category_meta   = CATEGORY_META,
        tips            = INTERVIEW_TIPS.get(result.category, []),
    )


# ──────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    user = get_current_user()
    return jsonify({
        "total":  user.total_attempts,
        "best":   user.best_score,
        "avg":    user.avg_score,
        "streak": user.streak,
    })


@app.route("/api/delete-result/<int:result_id>", methods=["POST"])
@login_required
def delete_result(result_id):
    user   = get_current_user()
    result = InterviewResult.query.filter_by(id=result_id, user_id=user.id).first()
    if result:
        db.session.delete(result)
        db.session.commit()
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 404


# ──────────────────────────────────────────────
# ERROR HANDLERS
# ──────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template("500.html"), 500


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get("FLASK_ENV") != "production")
