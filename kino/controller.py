import requests
from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Booking, Show, Tag, User, Venue, db

controller = Blueprint("controller", __name__)


@controller.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" in session:
        user = db.session.query(User).filter(
            User.username == session["user"]).first()
        if user.username == "admin":
            if request.method == "POST":
                pass
            else:
                return render_template("admin/index.html")
        else:
            redirect(url_for(controller.login))
    else:
        redirect(url_for(controller.login))


@controller.route("/", methods=["GET", "POST"])
def home():
    return render_template("user/index.html")


# test data
# U -> unbooked(available)
# B -> Booked
# T -> reserved but not confirmed(used in PUT/transient state)
seating_map = {
    "A": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
    "B": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
    "C": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
    "D": ["U", "T", "U", "U", "U", "U", "U", "U", "U", "U"],
    "E": ["B", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
}


@controller.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        pass
    else:
        return render_template("user/book.html", map=seating_map.items())


@controller.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("auth/signup.html", pwd_mismatch=True)

        user = User(
            name=name,
            role="user",
            username=username,
            password=generate_password_hash(password1),
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("controller.home"))


@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            return render_template("auth/login.html")
        else:
            if check_password_hash(user.password, password):
                session["user"] = user.username
                print(f"{username} Logged in!")
                if username == "admin":
                    return redirect(url_for("controller.admin"))
                else:
                    return redirect(url_for("controller.home"))
            else:
                return render_template("auth/login.html")


@controller.route("/logout", methods=["GET", "POST"])
def logout():
    if "user" in session:
        username = session.pop("user", None)
        print(f"{username} Logged out!")
        return redirect(url_for("controller.login"))


# End of File
