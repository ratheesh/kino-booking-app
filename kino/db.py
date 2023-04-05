from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash
from sqlalchemy import PrimaryKeyConstraint, func


Base = declarative_base()
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="user")
    profile_img = db.Column(db.String(32), default="default.png")
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())

    bookings = db.relationship("Booking", backref="user", cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="user", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return self.username

class Venue(db.Model):
    __tablename__ = "venue"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    place = db.Column(db.String(64), nullable=False)
    venue_img = db.Column(db.String(64), nullable=False, default="default.png")
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())

    shows = db.relationship("Show", backref="venue", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return self.name


show_tags = db.Table(
    "show_tags",
    db.Column("show_id", db.Integer, db.ForeignKey("show.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)

class Like(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return str(self.id)


class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    language = db.Column(db.String(32), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0.0)
    popularity = db.Column(db.Integer)
    show_time = db.Column(db.DateTime, nullable=False)
    n_rows = db.Column(db.Integer, nullable=False)
    n_seats = db.Column(
        db.Integer, nullable=False
    )  # seats per row -> not total no. of seats in the show
    show_img = db.Column(db.String(64), nullable=False, default="default.png")
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())

    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False)
    tags = db.relationship("Tag", secondary=show_tags, backref="shows")

    seats = db.relationship("Seat", backref="show", cascade="all,delete-orphan")
    bookings = db.relationship("Booking", backref="show", cascade="all,delete-orphan")

    likes = db.relationship("Like", backref="show", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return self.title


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(16), nullable=False)

    def __repr__(self) -> str:
        return self.name


class Seat(db.Model):
    __tablename__ = "seat"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    seat = db.Column(db.String(4), nullable=False)

    show_id = db.Column(db.Integer, db.ForeignKey("show.id", ondelete="CASCADE"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return self.seat


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    booking_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    # time = db.Column(db.String(64), nullable=False)
    final_amount = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id", ondelete="CASCADE"), nullable=False)
    seats = db.relationship("Seat", backref="booking", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return str(self.id) + " " + str(self.final_amount) + " " + str(self.user_id)


def create_admin_user(db):
    admin = User(
        name="Admin",
        username="admin",
        role="admin",
        password=generate_password_hash("admin"),
        created_timestamp=datetime.now(),
        updated_timestamp=datetime.now(),
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
