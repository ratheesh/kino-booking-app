from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import backref

engine = None
Base = declarative_base()
db = SQLAlchemy()


class User(db.Model):
    # __tablename__ = 'user',
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    dob = db.Column(db.String, unique=True, nullable=False)  # set to date obj
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    username = db.Column(db.String, nullable=False)
    passwd = db.Column(db.String, nullable=False)
    recovery_key = db.Column(db.String, nullable=False)
    created_on = db.Column(db.String, nullable=False)  # set to datetime obj
    tickets = db.relationship("Booking", backref="user")


class Venue(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, unique=True, nullable=False)
    shows = db.relationship("Show", backref="venue")


class Show(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lang = db.Column(db.String, nullable=False)
    certification = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String, nullable=False)
    tags = db.Column(db.String)
    show_date = db.Column(db.String, nullable=False)
    show_time = db.Column(db.String, nullable=False)
    banner_path = db.Column(db.String, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    tickets = db.relationship("Ticket", backref="show")


class Ticket(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    booked_at = db.Column(db.String, nullable=False)
    show_date = db.Column(db.String, nullable=False)
    show_time = db.Column(db.String, nullable=False)
    seat = db.Column(db.String, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"))


class Booking(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    booking_date = db.Column(db.String, nullable=False)
    booking_date = db.Column(db.String, nullable=False)
    booking_time = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    tickets = db.relationship("Ticket", backref="booking")


# End of File
