from flask import Blueprint, render_template, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request["username"]
        passwd = request["passwd"]
    else:
        return render_template("login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")


# End of File
