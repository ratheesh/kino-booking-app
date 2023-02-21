from flask import Blueprint, render_template, request

admin = Blueprint("admin", __name__)


@admin.route("/", methods=["GET"])
def main():
    return render_template("admin/index.html")


@admin.route("/venue", methods=["GET", "POST", "PUT", "DELETE"])
def book(venue_id=None):
    if request.method == "POST":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        pass
    else:
        return render_template("admin/venue.html")


# End of File
