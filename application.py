import os
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///people.db")

@app.route("/")
@login_required
def index():

    current_user_id = session["user_id"]

    username_dict = db.execute("SELECT username FROM people WHERE id = ?", current_user_id)
    this_username = username_dict[0]["username"].capitalize()

    courses = db.execute("SELECT * FROM marks WHERE user_id = ?", current_user_id)

    course_len = len(courses)

    return render_template("index.html", name=this_username, courses=courses, course_len=course_len)


@app.route("/addgrades", methods=["GET", "POST"])
@login_required
def addgrades():

    if request.method == "GET":
        return render_template("addgrades.html")

    elif request.method == "POST":

        current_user_id = session["user_id"]
        course = request.form.get("course")
        assignment_name = request.form.get("assignment_name")
        ib_grade = request.form.get("ib_grade")
        raw_mark = request.form.get("raw_mark")

        db.execute("INSERT INTO marks (user_id, courses, ib_mark, other_marks, assignment_name) VALUES (?,?,?,?,?)", current_user_id, course, ib_grade, raw_mark, assignment_name)

        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM people WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password:
            return apology("Username/password field(s) empty", 403)

        if password != confirm_password:
            return apology("Passwords do not match", 403)

        password_hash = generate_password_hash(password)

        db.execute("INSERT INTO people (username, hash) VALUES (:username, :hash)", username=username, hash=password_hash)

        return redirect("/login")

    return apology("TODO")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
