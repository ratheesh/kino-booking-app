from flask_login import UserMixin, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    image = db.Column(db.String(32))

    bookings = db.relationship("Booking", backref="user")

    def __repr__(self) -> str:
        return self.username


# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))


class Venue(db.Model):
    __tablename__ = "venue"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(32), nullable=False)

    shows = db.relationship("Show", backref="venue")

    def __repr__(self) -> str:
        return self.name


tags = db.Table(
    "tags",
    db.Column("show_id", db.Integer, db.ForeignKey("show.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)


class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    language = db.Column(db.String(32), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer)
    show_date = db.Column(db.String(64), nullable=False)
    show_time = db.Column(db.String(64), nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    seats = db.Column(
        db.Integer, nullable=False
    )  # seats per row -> not total no. of seats in the show
    banner_path = db.Column(db.String(64), nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    bookings = db.relationship("Booking", backref="show")
    show_tags = db.relationship("Tag", secondary=tags, backref="tag_tags")

    def __repr__(self) -> str:
        return self.name


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(16), nullable=False)

    def __repr__(self) -> str:
        return self.name


class Seat(db.Model):
    __tablename__ = "seat"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    rowno = db.Column(db.String(4), nullable=False)
    seatno = db.Column(db.String(4), nullable=False)

    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"))

    def __repr__(self) -> str:
        return self.row + self.seat


# class Likes(db.Model):
#     __tablename__ = "likes"
#     isliked = db.Column(db.Boolean, nullable=False)


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    booking_date = db.Column(db.String(64), nullable=False)
    booking_time = db.Column(db.String(64), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    seats = db.relationship("Seat", backref="booking")

    def __repr__(self) -> str:
        return self.date + " " + self.time


def create_admin_user(db):
    admin = User(
        name="Admin",
        username="admin",
        role="admin",
        password=generate_password_hash("iitm"),
    )
    db.session.add(admin)
    db.session.commit()


def populate_tags(db):
    tags = (
        "action",
        "comedy",
        "thriller",
        "crime",
        "scifi",
        "fantasy",
        "horror",
        "period",
        "romedy",
    )
    taglist = []

    for tag in tags:
        action = Tag(name=tag)
        taglist.append(action)

    db.session.add_all(taglist)
    db.session.commit()


# End of File
