# ElevateAI 🚀

ElevateAI is an AI-powered interview preparation platform built using Flask.  
It helps users practice interview questions, receive feedback, and track their performance.

---

## Features

- User Signup and Login
- Dashboard with interview statistics
- HR, Technical, and Communication interview categories
- Timed and Untimed interview modes
- AI-style feedback based on answers
- Interview score tracking
- Interview history with date
- Category-wise score tracking
- Dark / Light theme
- Responsive UI

---

## Tech Stack

Frontend:
- HTML
- CSS
- JavaScript
- Jinja Templates

Backend:
- Python
- Flask

Database:
- SQLite
- Flask-SQLAlchemy

Version Control:
- Git
- GitHub

---

## Project Structure

ElevateAI
│
├── app.py
├── README.md
│
├── instance
│   └── users.db
│
├── static
│   └── style.css
│
└── templates
    ├── base.html
    ├── dashboard.html
    ├── interview.html
    ├── login.html
    ├── mode.html
    ├── result.html
    └── signup.html

## Installation

Clone the repository

Navigate to the project folder

cd ElevateAI

Install dependencies:
pip install flask
pip install flask_sqlalchemy

Run the application

Open the browser and visit

http://127.0.0.1:5000


