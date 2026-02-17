from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ---------------- INTERVIEW RESULT TABLE ----------------
class InterviewResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Try another."

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", username=session["user"])
    return redirect(url_for("login"))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- QUESTIONS ----------------
questions = [
    "Tell me about yourself.",
    "What are your strengths?",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?"
]


# ---------------- INTERVIEW ----------------
@app.route("/interview", methods=["GET", "POST"])
def interview():
    if "user" not in session:
        return redirect(url_for("login"))

    if "q_index" not in session:
        session["q_index"] = 0

    if "answers" not in session:
        session["answers"] = []

    if request.method == "POST":
        answer = request.form["answer"]
        session["answers"].append(answer)
        session["q_index"] += 1

    if session["q_index"] >= len(questions):
        score = sum(1 for a in session["answers"] if len(a.strip().split()) >= 3)

        result = InterviewResult(
            username=session["user"],
            score=score,
            total=len(questions)
        )
        db.session.add(result)
        db.session.commit()

        session.pop("q_index", None)
        session.pop("answers", None)

        return render_template("result.html", score=score, total=len(questions))

    question = questions[session["q_index"]]
    return render_template("interview.html", question=question)

    if "user" not in session:
        return redirect(url_for("login"))

    if "q_index" not in session:
        session["q_index"] = 0

    if "answers" not in session:
        session["answers"] = []

    if request.method == "POST":
        answer = request.form["answer"]
        session["answers"].append(answer)
        session["q_index"] += 1

    # Finish interview → calculate score + save to DB
    if session["q_index"] >= len(questions):
        score = sum(1 for a in session["answers"] if len(a.strip().split()) >= 3)

        # Save history
        result = InterviewResult(
            username=session["user"],
            score=score,
            total=len(questions)
        )
        db.session.add(result)
        db.session.commit()

        session.pop("q_index", None)
        session.pop("answers", None)

        return render_template("result.html", score=score, total=len(questions))

    question = questions[session["q_index"]]
    return render_template("interview.html", question=question)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
