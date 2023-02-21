# from flask import Flask, request
from flask import Blueprint

# from flask import current_app as app


views = Blueprint("controller", __name__)


@views.route("/", methods=["GET", "POST"])
def venue():
    return "<h1> Venu Management </h1>"


@views.route("/user/signup", methods=["GET", "POST"])
def signup():
    return "<h1>User Signup</h1>"


@views.route("/user/login", methods=["GET", "POST"])
def login():
    return "<h1>User Login</h1>"


@views.route("/user/logout", methods=["GET", "POST"])
def logout():
    return "<h1>User Logout</h1>"


# End of File
