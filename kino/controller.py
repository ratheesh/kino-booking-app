import os
from datetime import datetime, timedelta
from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Booking, Seat, Show, Tag, User, Venue, db

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
            return redirect(url_for("controller.login", next=request.url))
        if current_user.role == "admin":
            return f(*args, **kwargs)

    return decorated_function


def user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "user":
            return redirect(url_for("controller.login", next=request.url))
        if current_user.role == "user":
            return f(*args, **kwargs)

    return decorated_function


@controller.route("/admin", methods=["GET", "POST"])
@login_required
@admin_only
def admin():
    if request.method == "POST":
        if "venue-management" in request.form:
            return redirect(url_for("controller.venue_management"))
        if "show-management" in request.form:
            return redirect(url_for("controller.show_management"))
    else:
        venue_count=Venue.query.count()
        show_count=Show.query.count()
        return render_template("admin/index.html", venue_count=venue_count, show_count=show_count)


@controller.route("/admin/venue", methods=["GET", "POST"])
@login_required
@admin_only
def venue_management():
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

        return redirect(url_for("controller.admin"))


@controller.route("/admin/venue/add", methods=["GET", "POST"])
@login_required
@admin_only
def venue_add():
    if request.method == "GET":
        return render_template("admin/venue_add.html")
    if request.method == "POST":
        name = request.form["name"]
        place = request.form["place"]
        venue = Venue(name=name, place=place, venue_img="default.png")
        db.session.add(venue)
        db.session.flush()

        venue_img_path = "default.png"
        if request.files["file"]:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file = request.files["file"]
            if not valid_img_type(file.filename):
                flash("img format is not supported", "danger")
                return render_template("admin/venue_add.html", pic_err=True)

            split_tup = os.path.splitext(file.filename)

            venue_img_path = os.path.join(
                basedir + "/static/img/venue/", str(venue.id) + split_tup[1]
            )
            print(venue_img_path)
            request.files["file"].save(venue_img_path)
            venue.venue_img = os.path.basename(venue_img_path)

        db.session.commit()
        flash("Venue Created Successfully!", "success")
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
        venue.place = request.form["place"]
        if request.files["file"]:
            venue_img_path = "default.png"
            if request.files["file"]:
                basedir = os.path.abspath(os.path.dirname(__file__))
                file = request.files["file"]
                if not valid_img_type(file.filename):
                    flash("img format is not supported", "danger")
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
        flash("Venue details Updated", "success")
        return redirect(url_for("controller.venue_management"))
    else:
        return redirect(url_for("controller.venue_management"))


@controller.route("/admin/venue/<int:venue_id>/delete", methods=["POST"])
@login_required
@admin_only
def venue_delete(venue_id):
    if request.method == "POST":
        venue = Venue.get_or_404(venue_id)
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            flash("Unable to delete Venue")
        flash("Venue deleted successfully")
        return redirect("controller.venue_management")
    else:
        abort(403)


@controller.route("/admin/<int:venue_id>/show", methods=["GET", "POST"])
@login_required
@admin_only
def show_management(venue_id):
    if request.method == "GET":
        venue = Venue.query.get_or_404(venue_id)
        shows = Show.query.filter_by(venue_id=venue_id).all()
        return render_template("admin/show.html", shows=shows, venue=venue)

    elif request.method == "POST":
        if "edit-show" in request.form:
            print("== SHOW EDIT ==")
            show_id = int(request.form["edit-show"])
            return redirect(
                url_for("controller.show_edit", venue_id=venue_id, show_id=show_id),
            )

        if "delete-show" in request.form:
            print("== SHOW DELETE ==")
            show_id = int(request.form["delete-show"])
            return redirect(
                url_for("controller.show_delete", venue_id=venue_id, show_id=show_id)
            )
        return redirect(url_for("controller.show_add", venue_id=venue_id))
    else:
        pass


@controller.route("/admin/<int:venue_id>/show/add", methods=["GET", "POST"])
@login_required
@admin_only
def show_add(venue_id):
    if request.method == "GET":
        tags = Tag.query.all()
        return render_template("admin/show_add.html", tags=tags, venue_id=venue_id)
    if request.method == "POST":
        print("== SHOW ADD ==")
        s_date = request.form["show_date"]
        s_time = request.form["show_time"]
        s_dt = datetime.strptime(s_date, "%Y-%m-%d")
        s_tm = datetime.strptime(s_time, "%H:%M").time()
        dt = datetime.combine(s_dt, s_tm)
        print(dt, type(dt))
        show = Show(
            title=request.form["title"],
            language=request.form["language"],
            duration=request.form["duration"],
            price=request.form["price"],
            rating=request.form["rating"],
            popularity=0,  # this should updated based on user ratings
            show_time=datetime.combine(s_dt, s_tm),
            n_rows=request.form["rows"],
            n_seats=request.form["seats"],
            venue_id=venue_id,
            show_img="default.png",
        )
        db.session.add(show)
        db.session.flush()

        show_img_path = "default.png"
        if request.files["file"]:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file = request.files["file"]
            if not valid_img_type(file.filename):
                flash("img format is not supported", "danger")
                return render_template("admin/show_add.html", pic_err=True)

            split_tup = os.path.splitext(file.filename)

            show_img_path = os.path.join(
                basedir + "/static/img/show/", str(show.id) + split_tup[1]
            )
            print(show_img_path)
            request.files["file"].save(show_img_path)
            show.venue_img = os.path.basename(show_img_path)

        tags = request.form.getlist("tags")
        for tag in tags:
            tg = Tag.query.filter_by(name=tag).first()
            if tg is None:
                abort(404)
            show.tags.append(tg)

        db.session.commit()

        flash("Show Created Successfully!", "success")
        return redirect(url_for("controller.show_management", venue_id=venue_id))


@controller.route(
    "/admin/<int:venue_id>/show/<int:show_id>/edit", methods=["GET", "POST"]
)
@login_required
@admin_only
def show_edit(venue_id, show_id):
    show = Show.query.filter_by(id=show_id).first()
    if request.method == "GET":
        if show is not None:
            return render_template("admin/show_add.html", show=show)
        else:
            abort(404)

    if request.method == "POST":
        s_date = request.form["show_date"]
        s_time = request.form["show_time"]
        s_dt = datetime.strptime(s_date, "%Y-%m-%d")
        s_tm = datetime.strptime(s_time, "%H:%M").time()
        dt = datetime.combine(s_dt, s_tm)
        print(dt, type(dt))

        show.title = (request.form["title"],)
        show.language = (request.form["language"],)
        show.duration = (request.form["duration"],)
        show.price = (request.form["price"],)
        show.popularity = (0,)  # this should updated based on user ratings
        show.show_time = (dt,)  # datetime.combine(s_dt, s_tm),
        show.n_rows = (request.form["rows"],)
        show.n_seats = (request.form["seats"],)
        show.venue_id = (venue_id,)
        show.show_img = ("default.png",)

        db.session.add(show)
        db.session.flush()

        show_img_path = "default.png"
        if request.files["file"]:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file = request.files["file"]
            if not valid_img_type(file.filename):
                flash("img format is not supported", "danger")
                return render_template("admin/show_add.html", show=show, pic_err=True)

            split_tup = os.path.splitext(file.filename)

            show_img_path = os.path.join(
                basedir + "/static/img/show/", str(show.id) + split_tup[1]
            )
            print(show_img_path)
            request.files["file"].save(show_img_path)
            show.venue_img = os.path.basename(show_img_path)

        db.session.commit()
        flash("Show details updated successfully!", "success")
        return redirect(url_for("controller.show_management", venue_id=venue_id))


# data
# {
#  "today": [show1, show2, ...],
#  "tomorrow": [show1, show2, ...],
#  "venues": {
#       "venue1": [show1, show2, ...]
#       "venue2":[show1, show2, ...]
#  },
# "tags": {
#  "tag1": [show1, show2, ...]
#  "tag2": [show1, show2, ...]
#  "tag3": [show1, show2, ...]
#  }
# }
#
@controller.route("/", methods=["GET", "POST"])
# @login_required
def home():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("controller.admin"))

    data = {}
    today = Show.query.filter(func.date(Show.show_time) == datetime.now().date()).all()
    data["today"] = today
    tomorrow = Show.query.filter(
        func.date(Show.show_time) == (datetime.now().date() + timedelta(days=+1))
    ).all()
    data["tomorrow"] = tomorrow
    data["venues"] = {}
    venues = Venue.query.all()
    for venue in venues:
        data["venues"][venue.name] = venue.shows

    data["tags"] = {}
    taglist = Tag.query.all()
    for tag in taglist:
        print(tag.name)
        data["tags"][tag.name] = tag.shows

    return render_template("user/index.html", data=data)


# test data
# B -> Booked
# U -> unbooked(available for booking)
# T -> reserved but not confirmed(used in PUT/transient state)
# seating_map = {
#     "A": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
#     "B": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
#     "C": ["U", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
#     "D": ["U", "T", "U", "U", "U", "U", "U", "U", "U", "U"],
#     "E": ["B", "U", "U", "U", "U", "U", "U", "U", "U", "U"],
# }


@controller.route("/<int:booking_id>/checkout", methods=["GET", "POST"])
@login_required
@user_only
def checkout(booking_id=None):
    if request.method == "POST":
        pass
    else:
        if booking_id:
            booking = Booking.query.get_or_404(booking_id)
            return render_template("/user/checkout.html", booking=booking)


def gen_seatingmap(show):
    print(show)
    init_row = "A"
    # map = dict.fromkeys(
    #     [chr(ord("A") + i) for i in range(show.n_rows)],
    #     ["U" for _ in range(show.n_seats)],
    # )
    map = {}
    for i in range(show.n_rows):
        map[chr(ord(init_row) + i)] = ["U" for _ in range(show.n_seats)]

    for seat in show.seats:
        print("seat:", seat)
        col = int(seat.seat[1:])
        row = seat.seat[0]
        map[row][col - 1] = "B"
        # print(map[row])

    # print(map)
    return map


@controller.route("/bookings", methods=["GET", "POST"])
@login_required
@user_only
def bookings():
    if request.method == "POST":
        pass
    else:
        _bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template("user/bookings.html", bookings=_bookings)


@controller.route("/<int:show_id>/book", methods=["GET", "POST"])
@login_required
@user_only
def book(show_id):
    show = Show.query.filter_by(id=show_id).first()
    print("Show: ", show)
    if show is None:
        flash(f"No show by id:{show_id}")
        return redirect(url_for("controller.home"))

    venue = Venue.query.filter_by(id=show.venue_id).first()
    print("Venue: ", venue)
    if venue is None:
        flash(f"no venue associated with the show:{show.title}")
        return redirect(url_for("controller.home"))

    if request.method == "POST":
        sel_seats = request.form.getlist("seat")
        print(sel_seats)
        if sel_seats == []:
            flash("No seats selected for booking", "warning")
            return render_template(
                "user/book.html",
                venue=venue,
                show=show,
                map=gen_seatingmap(show).items(),
            )
        else:
            booking = Booking(
                booking_time=datetime.now(),
                final_amount=len(sel_seats) * show.price,
                user_id=current_user.id,
            )
            db.session.add(booking)
            db.session.flush()

            seats_booked = []
            for seat in sel_seats:
                _seat = Seat(seat=seat, booking_id=booking.id, show_id=show_id)
                seats_booked.append(_seat)

            [print(seat) for seat in seats_booked]
            db.session.add_all(seats_booked)
            db.session.commit()
            flash("Booking Successful", "success")
            return redirect(url_for("controller.checkout", booking_id=booking.id))
    else:
        return render_template(
            "user/book.html", venue=venue, show=show, map=gen_seatingmap(show).items()
        )


@controller.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.username == "admin":
        flash("Admin profile can't be viewed", "danger")
        return redirect(url_for("controller.admin"))
    else:
        if request.method == "GET":
            return render_template("user/profile.html", user=current_user)
        if request.method == "POST":
            if "edit-profile" in request.form:
                return redirect(url_for("controller.profile_edit"))
            else:
                return redirect(url_for("controller.home"))


@controller.route("/profile/edit", methods=["GET", "POST"])
@login_required
@user_only
def profile_edit():
    if request.method == "GET":
        return render_template("user/profile_edit.html", user=current_user)
    if request.method == "POST":
        name = request.form["name"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != "" or password2 != "":
            if password1 != password2:
                flash("Passwords does not match!", "danger")
                return render_template("user/profile_edit.html", user=current_user)
        else:
            print(f"name:{name}, pass1={password1}, pass2={password2}")
            current_user.name = name
            current_user.password = generate_password_hash(password1)

        profile_img_path = "default.png"
        if request.files["file"]:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file = request.files["file"]
            if not valid_img_type(file.filename):
                flash("img format is not supported")
                return render_template("user/profile.html", pic_err=True)

            split_tup = os.path.splitext(file.filename)

            profile_img_path = os.path.join(
                basedir + "/static/img/profile/",
                str(current_user.id) + split_tup[1],
            )
            print(profile_img_path)
            request.files["file"].save(profile_img_path)
            current_user.profile_img = os.path.basename(profile_img_path)

        current_user.updated_timestamp = datetime.now()
        db.session.add(current_user)
        db.session.commit()
        flash("User details updated!", "success")
        return redirect(url_for("controller.profile", user=current_user))


@controller.route("/profile/delete", methods=["GET", "POST"])
@login_required
@user_only
def profile_delete():
    pass


@controller.route("/search", methods=["GET", "POST"])
@login_required
@user_only
def search():
    search = request.args.get("search")
    print("Searched:", search)
    if search is None:
        flash("search query is empty", "warning")
        return redirect(url_for("controller.home"))

    # venue_name = (
    #     db.session.query(Venue).filter(Venue.name.ilike("%" + search + "%")).all()
    # )
    # venue_place = (
    #     db.session.query(Venue).filter(Venue.place.ilike("%" + search + "%")).all()
    # )
    # show_title = (
    #     db.session.query(Show).filter(Show.title.ilike("%" + search + "%")).all()
    # )
    # show_language = (
    #     db.session.query(Show).filter(Show.language.ilike("%" + search + "%")).all()
    # )
    # show_rating = (
    #     db.session.query(Show).filter(Show.rating.ilike("%" + search + "%")).all()
    # )
    # show_popularity = (
    #     db.session.query(Show).filter(Show.popularity.ilike("%" + search + "%")).all()
    # )
    venues = (
        db.session.query(Venue)
        .filter(
            or_(
                Venue.name.ilike("%" + search + "%"),
                Venue.place.ilike("%" + search + "%"),
            )
        )
        .all()
    )

    shows = (
        db.session.query(Show).filter(
            or_(
                Show.title.ilike("%" + search + "%"),
                Show.language.ilike("%" + search + "%"),
                Show.rating.ilike("%" + search + "%"),
                Show.popularity.ilike("%" + search + "%"),
                # Show.tags.ilike("%" + search + "%"),
            )
        )
    ).all()

    # tags = db.session.query(Tag).filter(Tag.name.ilike("%" + search + "%")).all()

    print("Search Results: ", venues, shows)
    return render_template("/search.html", searched=search, venues=venues, shows=shows)


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
            flash("User name already exists!", "danger")
            return render_template("auth/signup.html")
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            flash("Passwords does not match!", "danger")
            return render_template("auth/signup.html")

        user = User(
            name=name,
            role="user",
            username=username,
            password=generate_password_hash(password1),
            profile_img="default.png",
            created_timestamp=datetime.now(),
            updated_timestamp=datetime.now(),
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

        # db.session.add(user)
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
            flash("User/password not matching!", "danger")
            return redirect(url_for("controller.login"))
        else:
            login_user(user)
            print(f"{user.username} logged in")
            flash(f"Welcome {user.name.capitalize()}!", "success")
            if current_user.username == "admin":
                return redirect(url_for("controller.admin"))
            else:
                return redirect(url_for("controller.home"))


@controller.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Bye till next time!", "success")
    return redirect(url_for("controller.home"))


@controller.errorhandler(404)
def page_not_found():
    return "page not found!"


@controller.errorhandler(500)
def internal_server_error():
    return "Internal Server Error!"


# End of File
