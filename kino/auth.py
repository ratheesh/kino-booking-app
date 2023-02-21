from flask import Blueprint, render_template, request

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
