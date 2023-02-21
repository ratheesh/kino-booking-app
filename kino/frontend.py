from flask import Blueprint, render_template, request

# from flask import current_app as app


frontend = Blueprint("frontend", __name__)


@frontend.route("/", methods=["GET", "POST"])
def main():
    return render_template("index.html")


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


@frontend.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        pass
    else:
        return render_template("book.html", map=seating_map.items())


@frontend.route("/user/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")


@frontend.route("/user/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@frontend.route("/user/logout", methods=["GET", "POST"])
def logout():
    return render_template("login.html", logout=True)


# End of File
