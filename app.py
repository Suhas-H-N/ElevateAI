"""
ElevateAI - AI-Powered Interview Preparation Platform
Final Year Project | Professional Production Build
"""

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os
import re

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

    def __repr__(self):
        return f"<User {self.username}>"


class InterviewResult(db.Model):
    __tablename__ = "interview_results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default="medium")
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Result {self.category} {self.score}/{self.total}>"


# ──────────────────────────────────────────────
# QUESTION BANK (Difficulty-Aware)
# ──────────────────────────────────────────────
QUESTION_BANK = {
    "hr": {
        "easy": [
            "Tell me about yourself.",
            "What are your hobbies and interests?",
            "Why did you choose your field of study?",
            "Describe yourself in three words.",
        ],
        "medium": [
            "Why should we hire you over other candidates?",
            "What are your greatest strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Describe a time you worked in a team.",
        ],
        "hard": [
            "Tell me about a time you failed and what you learned.",
            "How do you handle conflict with a teammate or supervisor?",
            "Describe a situation where you had to adapt quickly to change.",
            "What's your strategy for managing multiple competing priorities?",
        ],
    },
    "technical": {
        "easy": [
            "What is Object-Oriented Programming?",
            "Explain the difference between a list and a tuple in Python.",
            "What is a database and why is it used?",
            "What is an API and give an example of how it's used.",
        ],
        "medium": [
            "Explain the difference between SQL and NoSQL databases.",
            "What is the MVC design pattern and where is it used?",
            "Explain time complexity and give an example of O(n log n).",
            "What is the difference between authentication and authorization?",
        ],
        "hard": [
            "Explain CAP theorem and how it applies to distributed systems.",
            "How does a hash table work internally, and what causes collisions?",
            "Describe the microservices architecture and its trade-offs vs. monoliths.",
            "How would you design a URL shortening service like bit.ly?",
        ],
    },
    "communication": {
        "easy": [
            "Describe your favorite project in simple terms.",
            "How do you explain a technical topic to a non-technical person?",
            "Tell me about a time you helped a friend or colleague.",
            "What motivates you to do your best work?",
        ],
        "medium": [
            "How do you handle pressure and tight deadlines?",
            "Describe a situation where you had to deliver difficult news.",
            "How do you give and receive constructive feedback?",
            "Describe your communication style when working in a diverse team.",
        ],
        "hard": [
            "Describe a situation where your communication prevented a major mistake.",
            "How would you resolve a misunderstanding between two departments?",
            "Tell me about a time you had to persuade stakeholders to change direction.",
            "How do you ensure clarity when communicating complex decisions remotely?",
        ],
    },
}

CATEGORY_META = {
    "hr": {"icon": "👔", "label": "HR Round", "color": "#6366F1", "description": "Behavioral & personality questions"},
    "technical": {"icon": "⚙️", "label": "Technical Round", "color": "#0EA5E9", "description": "Core CS & engineering concepts"},
    "communication": {"icon": "💬", "label": "Communication Round", "color": "#10B981", "description": "Soft skills & situational questions"},
}

DIFFICULTY_META = {
    "easy": {"label": "Easy", "color": "#22C55E", "icon": "🟢"},
    "medium": {"label": "Medium", "color": "#F59E0B", "icon": "🟡"},
    "hard": {"label": "Hard", "color": "#EF4444", "icon": "🔴"},
}


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


def generate_feedback(answers, difficulty="medium"):
    """
    Rule-based feedback engine that evaluates answers based on content quality,
    structure, and length relative to difficulty expectations.
    """
    thresholds = {"easy": 10, "medium": 20, "hard": 35}
    min_words = thresholds.get(difficulty, 20)

    feedback = []
    for ans in answers:
        ans = ans.strip()
        word_count = len(ans.split()) if ans else 0

        if word_count == 0:
            feedback.append({
                "rating": "skipped",
                "icon": "⚠️",
                "text": "No answer provided. Always attempt every question — partial credit is better than none."
            })
        elif word_count < 5:
            feedback.append({
                "rating": "poor",
                "icon": "❌",
                "text": f"Answer too brief ({word_count} words). Use the STAR method: Situation, Task, Action, Result."
            })
        elif word_count < min_words:
            feedback.append({
                "rating": "fair",
                "icon": "⚡",
                "text": f"Decent attempt ({word_count} words), but could use more depth. Add specific examples and context."
            })
        elif word_count < min_words * 2:
            feedback.append({
                "rating": "good",
                "icon": "✅",
                "text": f"Good answer ({word_count} words). Clear and structured. Try adding a concrete outcome or metric."
            })
        else:
            feedback.append({
                "rating": "excellent",
                "icon": "🌟",
                "text": f"Excellent response ({word_count} words). Comprehensive, detailed, and well-articulated."
            })

    return feedback


def get_performance_label(percentage):
    if percentage == 100:
        return {"label": "Perfect Score!", "icon": "🏆", "cls": "perfect"}
    elif percentage >= 75:
        return {"label": "Outstanding", "icon": "🌟", "cls": "excellent"}
    elif percentage >= 50:
        return {"label": "Good Progress", "icon": "👍", "cls": "good"}
    elif percentage >= 25:
        return {"label": "Keep Practicing", "icon": "⚡", "cls": "fair"}
    else:
        return {"label": "Needs Improvement", "icon": "💪", "cls": "improve"}


def get_current_user():
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])


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
            flash(f"Welcome back, {user.name or user.username}!", "success")
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
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        errors = []

        if not username or not email or not password:
            errors.append("All fields are required.")
        elif len(username) < 3 or len(username) > 30:
            errors.append("Username must be 3–30 characters.")
        elif not re.match(r"^[a-z0-9_]+$", username):
            errors.append("Username can only contain letters, numbers, and underscores.")
        elif not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        elif not is_strong_password(password):
            errors.append("Password must be at least 8 characters, include 1 uppercase letter and 1 number.")
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

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You've been signed out.", "info")
    return redirect(url_for("login"))


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

        user.gender = request.form.get("gender", "")
        user.college = request.form.get("college", "").strip()
        user.degree = request.form.get("degree", "").strip()
        user.branch = request.form.get("branch", "").strip()
        user.year_of_study = request.form.get("year_of_study", "")
        user.profession = request.form.get("profession", "")
        user.profile_complete = True

        db.session.commit()
        flash("Profile saved successfully!", "success")
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

    total_attempts = len(results)
    best_score = max((r.percentage for r in results), default=0)
    avg_score = round(sum(r.percentage for r in results) / total_attempts, 1) if results else 0

    # Chart data
    chart_labels = [r.date.strftime("%d %b") for r in results]
    chart_scores = [r.percentage for r in results]

    # Category breakdown
    cat_stats = {}
    for r in results:
        cat = r.category
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "attempts": 0}
        cat_stats[cat]["total"] += r.percentage
        cat_stats[cat]["attempts"] += 1

    category_averages = {
        cat: round(v["total"] / v["attempts"], 1)
        for cat, v in cat_stats.items()
    }

    return render_template(
        "dashboard.html",
        user=user,
        results=results,
        total_attempts=total_attempts,
        best_score=round(best_score, 1),
        avg_score=avg_score,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
        category_averages=category_averages,
        category_meta=CATEGORY_META,
        difficulty_meta=DIFFICULTY_META,
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
    )


@app.route("/interview", methods=["GET", "POST"])
@login_required
def interview():
    category = request.args.get("category", session.get("interview_category"))
    difficulty = request.args.get("difficulty", session.get("interview_difficulty", "medium"))

    # Initialize new session on fresh start
    if category and request.method == "GET" and request.args.get("category"):
        if category not in QUESTION_BANK or difficulty not in QUESTION_BANK.get(category, {}):
            flash("Invalid interview configuration.", "danger")
            return redirect(url_for("dashboard"))
        session["interview_category"] = category
        session["interview_difficulty"] = difficulty
        session["interview_q_index"] = 0
        session["interview_answers"] = []

    # Guard: must have active interview session
    if "interview_category" not in session:
        return redirect(url_for("dashboard"))

    cat = session["interview_category"]
    diff = session["interview_difficulty"]
    questions = QUESTION_BANK[cat][diff]

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        answers = session.get("interview_answers", [])
        answers.append(answer)
        session["interview_answers"] = answers
        session["interview_q_index"] = session.get("interview_q_index", 0) + 1

    q_index = session.get("interview_q_index", 0)

    # Interview complete → generate results
    if q_index >= len(questions):
        answers = session.get("interview_answers", [])
        feedback_list = generate_feedback(answers, diff)

        # Score: count "good" or "excellent" answers
        score = sum(1 for f in feedback_list if f["rating"] in ("good", "excellent"))
        total = len(questions)
        percentage = round((score / total) * 100, 1) if total > 0 else 0

        user = get_current_user()
        result = InterviewResult(
            user_id=user.id,
            category=cat,
            difficulty=diff,
            score=score,
            total=total,
            percentage=percentage,
        )
        db.session.add(result)
        db.session.commit()

        # Clear only interview state, not login session
        for key in ["interview_category", "interview_difficulty", "interview_q_index", "interview_answers"]:
            session.pop(key, None)

        performance = get_performance_label(percentage)

        # Pre-zip for Jinja2 (zip/enumerate not available by default)
        feedback_with_qa = list(zip(feedback_list, questions, answers))

        return render_template(
            "result.html",
            score=score,
            total=total,
            percentage=percentage,
            category=cat,
            difficulty=diff,
            feedback_with_qa=feedback_with_qa,
            performance=performance,
            meta=CATEGORY_META[cat],
            difficulty_meta=DIFFICULTY_META[diff],
        )

    question = questions[q_index]
    return render_template(
        "interview.html",
        question=question,
        current=q_index + 1,
        total=len(questions),
        category=cat,
        difficulty=diff,
        meta=CATEGORY_META[cat],
        difficulty_meta=DIFFICULTY_META[diff],
        progress=round(((q_index) / len(questions)) * 100),
    )


# ──────────────────────────────────────────────
# API ENDPOINT (for AJAX)
# ──────────────────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    user = get_current_user()
    results = InterviewResult.query.filter_by(user_id=user.id).all()
    return jsonify({
        "total": len(results),
        "best": max((r.percentage for r in results), default=0),
        "avg": round(sum(r.percentage for r in results) / len(results), 1) if results else 0,
    })


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
