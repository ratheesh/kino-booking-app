from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.orm import backref

engine = None
Base = declarative_base()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    passwd = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    created_on = db.Column(db.String, nullable=False)

    bookings = db.relationship("Booking", backref="user")


class Venue(db.Model):
    __tablename__ = "venue"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, unique=True, nullable=False)

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
    name = db.Column(db.String, nullable=False)
    language = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String)
    show_date = db.Column(db.String, nullable=False)
    show_time = db.Column(db.String, nullable=False)
    banner_path = db.Column(db.String, nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    tickets = db.relationship("Ticket", backref="show")
    show_tags = db.relationship("Tag", secondary=tags, backref="tag_tags")

    def __repr__(self) -> str:
        return self.name


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    def __repr__(self) -> str:
        return self.name


class Ticket(db.Model):
    __tablename__ = "ticket"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # booked_at = db.Column(db.String, nullable=False)

    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"))
    seats = db.relationship("Seat", backref="ticket")


class Seat(db.Model):
    __tablename__ = "seat"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    row = db.Column(db.String, nullable=False)
    seat = db.Column(db.String, nullable=False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"))


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    booking_date = db.Column(db.String, nullable=False)
    booking_time = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    tickets = db.relationship("Ticket", backref="booking")


# End of File
