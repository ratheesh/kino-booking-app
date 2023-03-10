import os
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Show, User, Venue, db

# from .forms import ShowForm

controller = Blueprint("controller", __name__)


def valid_img_type(filename):
    # return "." in filename and filename.rsplit(".", 1)[1].lower() in [
    #     "png",
    #     "jpg",
    #     "jpeg",
    # ]
    split_tup = os.path.splitext(filename)
    print("extension: " + split_tup[1][1:])
    return split_tup[1][1:] in ["png", "jpg", "jpeg"]


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            return redirect(url_for("auth.login", next=request.url))
        if current_user.role == "admin":
            return f(*args, **kwargs)

    return decorated_function


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
@admin_only
def venue_management():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "GET":
            venues = Venue.query.all()
            return render_template("admin/venue.html", venues=venues)

        if request.method == "POST":
            if "add-venue" in request.form:
                print("== VENUE ADD ==")
                return redirect(url_for("controller.venue_add"))
            if "manage-show" in request.form:
                print("== VENUE SHOW MGMT ==")
                return redirect(
                    url_for(
                        "controller.show_management",
                        venue_id=int(request.form["manage-show"]),
                    )
                )
            if "edit-venue" in request.form:
                print("== VENUE EDIT ==")
                return redirect(
                    url_for(
                        "controller.venue_edit",
                        venue_id=int(request.form["edit-venue"]),
                    )
                )

            if "delete-venue" in request.form:
                print("== VENUE DELETE ==")
                return redirect(
                    url_for(
                        "controller.venue_delete",
                        venue_id=int(request.form["delete-venue"]),
                    )
                )

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
            venue = Venue(name=name, city=city, venue_img="default.png")
            db.session.add(venue)
            db.session.flush()

            venue_img_path = "default.png"
            if request.files["file"]:
                basedir = os.path.abspath(os.path.dirname(__file__))
                file = request.files["file"]
                if not valid_img_type(file.filename):
                    flash("img format is not supported")
                    return render_template("admin/venue_add.html", pic_err=True)

                split_tup = os.path.splitext(file.filename)

                venue_img_path = os.path.join(
                    basedir + "/static/img/venue/", str(venue.id) + split_tup[1]
                )
                print(venue_img_path)
                request.files["file"].save(venue_img_path)
                venue.venue_img = os.path.basename(venue_img_path)

            db.session.commit()
            return redirect(url_for("controller.venue_management"))


@controller.route("/admin/venue/<int:venue_id>/edit", methods=["GET", "POST"])
@login_required
@admin_only
def venue_edit(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    if request.method == "GET":
        return render_template("admin/venue_edit.html", venue=venue)
    elif request.method == "POST":
        venue.name = request.form["name"]
        venue.city = request.form["city"]
        if request.files["file"]:
            venue_img_path = "default.png"
            if request.files["file"]:
                basedir = os.path.abspath(os.path.dirname(__file__))
                file = request.files["file"]
                if not valid_img_type(file.filename):
                    flash("img format is not supported")
                    return render_template("admin/venue_add.html", pic_err=True)

                split_tup = os.path.splitext(file.filename)

                venue_img_path = os.path.join(
                    basedir + "/static/img/venue/", str(venue.id) + split_tup[1]
                )
                print(venue_img_path)
                request.files["file"].save(venue_img_path)
                venue.venue_img = os.path.basename(venue_img_path)

        db.session.add(venue)
        db.session.commit()
        return redirect(url_for("controller.venue_management"))
    else:
        return redirect(url_for("controller.venue_management"))


@controller.route("/admin/venue/<int:venue_id>/delete", methods=["POST"])
@login_required
def venue_delete():
    if current_user.username != "admin":
        return redirect(url_for("controller.login"))
    else:
        if request.method == "POST":
            return "admin venue delete message"
        else:
            return f"This method does not support non-post methods-{request.method()}"


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
                poster_img="show.png",
            )
            db.session.add(show)
            db.session.commit()
            return redirect(url_for("controller.show_management", venue_id=venue_id))
            # return render_template("admin/show.html")


@controller.route("/", methods=["GET", "POST"])
# @login_required
def home():
    shows = Show.query.all()
    return render_template("user/index.html", shows=shows)


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
def book(show_id):
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
            if password1 != "" or password2 != "":
                if password1 != password2:
                    flash("Passwords does not match!", "error")
                    return render_template("user/profile_edit.html", user=current_user)
            else:
                print(f"name:{name}, pass1={password1}, pass2={password2}")
                current_user.name = name
                current_user.password = generate_password_hash(password1)

            if request.files["file"]:
                if not valid_img_type(request.files["file"].filename):
                    flash("Image type not supported", "error")
                    return render_template("auth/signup.html", img_error=True)
                request.files["file"].save(
                    os.path.join(
                        app.config["IMGFOLDER"] + "/profile /",
                        str(current_user.id) + ".jpg",
                    )
                )

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
        profile_img = "default.png"
        name = request.form["name"]
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash("User name already exists!", "error")
            return render_template("auth/signup.html")
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
            profile_img="default.png",
        )
        db.session.add(user)
        db.session.flush()

        venue_img_path = "default.png"
        if request.files["file"]:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file = request.files["file"]
            if not valid_img_type(file.filename):
                flash("img format is not supported")
                return render_template("auth/signup.html", pic_err=True)

            split_tup = os.path.splitext(file.filename)

            profile_img_path = os.path.join(
                basedir + "/static/img/profile/", str(user.id) + split_tup[1]
            )
            print(profile_img_path)
            request.files["file"].save(profile_img_path)
            profile.venue_img = venue_img_path
        db.session.add(user)
        db.session.commit()
        flash(f"{user.name}'s Profile created successfully!", "success")
        return redirect(url_for("controller.login"))


@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(request.form)
        user = db.session.query(User).filter(User.username == username).first()
        if not user or not check_password_hash(user.password, password):
            flash("User/password not matching!")
            return render_template("auth/login.html")
        else:
            login_user(user)
            print(f"{user.username} logged in")
            flash("Logged in!")
            if current_user.username == "admin":
                return redirect(url_for("controller.admin"))
            else:
                return redirect(url_for("controller.home"))


@controller.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("controller.home"))


@controller.errorhandler(404)
def page_not_found():
    return "page not found!"


@controller.errorhandler(500)
def internal_server_error():
    return "Internal Server Error!"


# End of File
