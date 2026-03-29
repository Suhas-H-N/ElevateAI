from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# ✅ FIXED SECRET KEY (important for sessions)
app.secret_key = "supersecretkey123"  # change later for production

# ---------------- DATABASE CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ---------------- INTERVIEW RESULT TABLE ----------------
class InterviewResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- AI FEEDBACK FUNCTION ----------------
def generate_feedback(answers):
    feedback = []
    for ans in answers:
        word_count = len(ans.strip().split())

        if word_count == 0:
            feedback.append("You skipped this question.")
        elif word_count < 3:
            feedback.append("Answer too short. Try to elaborate.")
        elif word_count < 8:
            feedback.append("Good, but you can explain more clearly.")
        else:
            feedback.append("Strong answer with good detail.")

    return feedback

# ---------------- QUESTION BANK ----------------
question_bank = {
    "hr": [
        "Tell me about yourself.",
        "Why should we hire you?",
        "What are your strengths?",
        "Where do you see yourself in 5 years?"
    ],
    "technical": [
        "Explain OOP concepts.",
        "What is a database?",
        "Difference between list and tuple.",
        "What is Flask?"
    ],
    "communication": [
        "Describe your favorite project.",
        "How do you handle pressure?",
        "Explain teamwork in your words.",
        "Describe a challenge you faced."
    ]
}

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if len(password) < 5:
            flash("Password must be at least 5 characters", "warning")
            return redirect(url_for("signup"))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    results = InterviewResult.query.filter_by(username=session["user"]).all()

    total_attempts = len(results)
    best_score = max([r.score for r in results], default=0)

    return render_template(
        "dashboard.html",
        username=session["user"],
        results=results,
        total_attempts=total_attempts,
        best_score=best_score
    )

# ---------------- MODE ----------------
@app.route("/mode")
def mode():
    if "user" not in session:
        return redirect(url_for("login"))

    category = request.args.get("category")
    return render_template("mode.html", category=category)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

# ---------------- INTERVIEW ----------------
@app.route("/interview", methods=["GET", "POST"])
def interview():
    if "user" not in session:
        return redirect(url_for("login"))

    category = request.args.get("category")
    mode = request.args.get("mode", "medium")

    # Reset if new category or mode
    if category and (session.get("category") != category or session.get("mode") != mode):
        session["category"] = category
        session["mode"] = mode
        session["q_index"] = 0
        session["answers"] = []

    if "category" not in session:
        return redirect(url_for("dashboard"))

    questions = question_bank[session["category"]]

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        session["answers"].append(answer)
        session["q_index"] += 1

    # Finish interview
    if session["q_index"] >= len(questions):
        answers = session["answers"]

        score = sum(1 for a in answers if len(a.split()) >= 3)
        feedback_list = generate_feedback(answers)

        result = InterviewResult(
            username=session["user"],
            category=session["category"],
            score=score,
            total=len(questions)
        )
        db.session.add(result)
        db.session.commit()

        session.pop("q_index", None)
        session.pop("answers", None)
        category = session.pop("category", None)
        mode = session.pop("mode", None)

        return render_template(
            "result.html",
            score=score,
            total=len(questions),
            feedback_list=feedback_list,
            category=category,
            mode=mode
        )

    question = questions[session["q_index"]]

    return render_template(
        "interview.html",
        question=question,
        current=session["q_index"] + 1,
        total=len(questions)
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)