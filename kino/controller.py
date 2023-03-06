from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Booking, Show, Tag, User, Venue, db
from .forms import ShowForm

controller = Blueprint("controller", __name__)


@controller.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "POST":
            if "venue-management" in request.form:
                return redirect(url_for("controller.venue_management"))
            if "show-management" in request.form:
                return redirect(url_for("controller.show_management"))
        else:
            return render_template("admin/index.html")


@controller.route("/admin/venue", methods=["GET", "POST"])
@login_required
def venue_management(venue_id=None):
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            venues = Venue.query.all()
            return render_template("admin/venue.html", venues=venues)

        if request.method == "POST":
            print(request.form)
            if "add-venue" in request.form:
                print("== VENUE ADD ==")
                return redirect(url_for("controller.venue_add"))
            if "manage-venue" in request.form:
                print("== VENUE SHOW MGMT ==")
                return redirect(
                    url_for("controller.show_management",
                            venue_id=int(venue_id))
                )
            if "edit-venue" in request.form:
                print("== VENUE EDIT ==")
                return redirect(url_for("controller.venue_edit"))

            # return redirect(url_for("controller.venue_add"))


@controller.route("/admin/venue/add", methods=["GET", "POST"])
@login_required
def venue_add():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            return render_template("admin/venue_add.html")
        if request.method == "POST":
            name = request.form["name"]
            city = request.form["city"]
            venue = Venue(name=name, city=city)
            db.session.add(venue)
            db.session.commit()
            return redirect(url_for("controller.venue_management"))


@controller.route("/admin/venue/<int:venue_id>/edit", methods=["GET", "POST"])
@login_required
def venue_update():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            return render_template("admin/venue_edit.html")
        elif request.method == "POST":
            return "admin venue post message"
        else:
            pass


@controller.route("/admin/venue/<int:venue_id>", methods=["DELETE"])
@login_required
def venue_delete():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            return render_template("admin/venue_create.html")
        elif request.method == "POST":
            return "admin venue post message"
        else:
            pass


@controller.route("/admin/<int:venue_id>/show", methods=["GET", "POST"])
@login_required
def show_management(venue_id):
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            shows = Show.query.filter_by(venue_id=venue_id).all()
            return render_template("admin/show.html", shows=shows, venue_id=venue_id)

        elif request.method == "POST":
            return redirect(url_for("controller.show_add", venue_id=venue_id))
        else:
            pass


@controller.route("/admin/<int:venue_id>/show/add", methods=["GET", "POST"])
@login_required
def show_add(venue_id):
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            return render_template("admin/show_add.html")
        if request.method == "POST":
            print("== SHOW ADD ==")
            show = Show(
                title=request.form["title"],
                language=request.form["language"],
                duration=request.form["duration"],
                price=request.form["price"],
                popularity=0,  # this should updated based on user ratings
                show_date=request.form["show_date"],
                show_time=request.form["show_time"],
                rows=request.form["rows"],
                seats=request.form["seats"],
                venue_id=venue_id,
                banner_path="show.png",
            )
            db.session.add(show)
            db.session.commit()
            return redirect(url_for("controller.show_management", venue_id=venue_id))
            # return render_template("admin/show.html")


@controller.route("/", methods=["GET", "POST"])
# @login_required
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


@controller.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.username == "admin":
        flash("Admin profile can't be viewed", "error")
    else:
        if request.method == "GET":
            return render_template("user/profile.html", user=current_user)
        if request.method == "POST":
            return redirect(url_for("controller.profile_edit"))


@controller.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    if current_user.username == "admin":
        flash("Admin profile can't be edited", "error")
    else:
        # user = User.query.filter_by(username=current_user.username)
        if request.method == "GET":
            return render_template("user/profile_edit.html", user=current_user)
        if request.method == "POST":
            name = request.form["name"]
            password1 = request.form["password1"]
            password2 = request.form["password2"]
            if password1 != password2:
                flash("Passwords does not match!", "error")
                return render_template("user/profile_edit.html", user=current_user)

            # current_user = User.query.filter_by(username=current_user.username)
            print(f"name:{name}, pass1={password1}, pass2={password2}")
            current_user.name = name
            current_user.password = generate_password_hash(password1)
            # db.session.add(user)
            db.session.commit()
            flash("User details updated!", "success")
            return redirect(url_for("controller.profile", user=current_user))


@controller.route("/profile/delete", methods=["GET", "POST"])
@login_required
def profile_delete():
    if current_user.username == "admin":
        flash("Admin profile can't be delete", "error")
    else:
        pass


@controller.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash(
                "username is already existed, Goto <a href={{url_for('controller.login')}}>Login page</a>",
                "error",
            )
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            flash("Passwords does not match!", "error")
            return render_template("auth/signup.html")

        user = User(
            name=name,
            role="user",
            username=username,
            password=generate_password_hash(password1),
        )
        db.session.add(user)
        db.session.commit()
        flash(f"{user.name}'s profile created successfully!", "success")
        return redirect(url_for("controller.login"))


@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter(User.username == username).first()
        if not user or not check_password_hash(user.password, password):
            flash("User/password not matching. Recheck your credentials!")
            return render_template("auth/login.html")
        else:
            login_user(user)
            print(f"{user.username} logged in")
            if current_user.username == "admin":
                return redirect(url_for("controller.admin"))
            else:
                return redirect(url_for("controller.home"))


@controller.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    print("Logged out!")
    return redirect(url_for("controller.home"))


@controller.errorhandler(404)
def page_not_found():
    return "page not found!"


@controller.errorhandler(500)
def internal_server_error():
    return "Internal Server Error!"


# End of File
