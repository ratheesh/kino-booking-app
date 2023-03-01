from datetime import datetime

from flask import Blueprint, make_response
from flask_httpauth import HTTPBasicAuth
from flask_restful import NotFound, Resource, fields, marshal_with, reqparse
from sqlalchemy import delete
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Booking, Show, Tag, User, Venue, db

# from flask_sqlalchemy import SQLAlchemy

auth = HTTPBasicAuth()
api = Blueprint("api", __name__)

hapi = None


class UnAuthorizedAccess(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 401)


class BadRequest(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 400)


class NotFoundError(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 404)


user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("name", type=str)
user_request_parse.add_argument("username", type=str)
user_request_parse.add_argument("password", type=str)
user_request_parse.add_argument("email", type=str)
# user_request_parse.add_argument("created_on", type=str)

user_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "username": fields.String,
    "password": fields.String,
    "email": fields.String,
    "created_on": fields.String,
}


@auth.verify_password
def verify_password(username, password):
    print("user:", username, "pass: ", password)
    user = db.session.query(User).filter(User.username == username).first()
    print(user)
    if username == user.username and check_password_hash(user.password, password):
        print("authentication successful!")
        return username


@auth.get_user_roles
def get_user_roles(user: User):
    if user.name == "admin":
        return "admin"
    else:
        return "user"


class UserAPI(Resource):
    @marshal_with(user_response_fields)
    def get(self, user_id=None):
        if user_id is not None:
            user_details = db.session.query(
                User).filter(User.id == user_id).first()

            if user_details:
                return user_details
            else:
                raise NotFoundError(msg="User not found")
        else:  # send details of all users
            users = db.session.query(User).all()
            # print(users)
            return users

    @marshal_with(user_response_fields)
    def post(self):
        args = user_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        username = args.get("username", None)
        password = generate_password_hash(args.get("password", None))
        email = args.get("email", None)
        # created_on = args.get("created_on", None)
        if (
            args is None
            or name is None
            or username is None
            or password is None
            or email is None
        ):
            raise BadRequest("incorrect argument")

        # check if the user already exists based on username
        _user = db.session.query(User).filter(
            User.username == username).first()
        if _user is not None:
            print("=== user already exists === ")
            raise BadRequest("user already exists")

        _user = User(
            name=name,
            role="user",
            username=username,
            password=password,
            email=email,
            created_on=datetime.now(),
        )
        db.session.add(_user)
        db.session.commit()

        return _user, 201

    @marshal_with(user_response_fields)
    def put(self, user_id):
        if user_id is None:
            pass  # return error
        else:
            args = user_request_parse.parse_args(strict=True)
            name = args.get("name", None)
            password = generate_password_hash(args.get("password", None))
            email = args.get("email", None)

            _user = db.session.query(User).filter(User.id == user_id).first()
            if _user is not None:
                _user.name = name
                _user.password = password
                _user.email = email
            else:
                raise NotFoundError("user not found")

            db.session.add(_user)
            db.session.commit()
            return _user

    def delete(self, user_id):
        if user_id is None:
            raise BadRequest("user id missing")
        else:
            _user = db.session.query(User).filter(User.id == user_id)
            if _user is None:
                raise NotFoundError("user not found")
            else:
                db.session.delete(_user)
                db.session.commit()


venue_request_parse = reqparse.RequestParser()
venue_request_parse.add_argument("name", type=str, required=True)
venue_request_parse.add_argument("city", type=str, required=True)

venue_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "city": fields.String,
}


class VenueAPI(Resource):
    @marshal_with(venue_response_fields)
    # @auth.login_required(role="admin")
    def get(self, venue_id=None):
        if venue_id is not None:
            _venue = db.session.query(Venue).filter(
                Venue.id == venue_id).first()

            if _venue:
                return _venue
            else:
                raise NotFoundError(status_code=404)
        else:
            venues = db.session.query(Venue).all()
            print(Venue)
            return venues

    @marshal_with(venue_response_fields)
    def post(self):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        city = args.get("city", None)

        print("name", name)
        print("city", city)

        _venue = Venue(
            name=name,
            city=city,
        )
        db.session.add(_venue)
        db.session.commit()

        return _venue, 201

    @marshal_with(venue_response_fields)
    def put(self, venue_id):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        city = args.get("city", None)
        if name is None:
            raise BadRequest("name is missing")
        if city is None:
            raise BadRequest("city is missing")

        venue_details = db.session.query(
            Venue).filter(Venue.id == venue_id).first()

        if venue_details:
            venue_details.name = name
            venue_details.city = city
        else:
            raise NotFoundError(status_code=404)

        db.session.add(venue_details)
        db.session.commit()

    def delete(self, venue_id):
        if venue_id is None:
            raise BadRequest("id is missing")
        else:
            venue = db.session.query(Venue).filter(
                Venue.id == venue_id).first()
            if venue is None:
                raise NotFoundError("venue not found")
            else:
                db.session.delete(venue)
                db.session.commit()


show_request_parse = reqparse.RequestParser()
show_request_parse.add_argument("name", type=str)
show_request_parse.add_argument("language", type=str)
show_request_parse.add_argument("duration", type=int)
show_request_parse.add_argument("rating", type=str)
show_request_parse.add_argument("price", type=int)
show_request_parse.add_argument("popularity", type=int)
show_request_parse.add_argument("genre", type=str)
show_request_parse.add_argument("show_date", type=str)
show_request_parse.add_argument("show_time", type=str)
show_request_parse.add_argument("banner_path", type=str)


show_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "language": fields.String,
    "duration": fields.Integer,
    "rating": fields.String,
    "price": fields.Integer,
    "popularity": fields.Integer,
    "genre": fields.String,
    "show_date": fields.String,
    "show_time": fields.String,
    "banner_path": fields.String,
}


class ShowAPI(Resource):
    @marshal_with(show_response_fields)
    def get(self, venue_id, show_id=None):
        if venue_id is None:
            raise BadRequest("venue id null")

        _venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if _venue is None:
            raise BadRequest("venue not found")

        if show_id is not None:
            _show = (
                db.session.query(Show)
                .filter(Show.id == show_id and _venue.id == venue_id)
                .first()
            )
            if _show is None:
                raise NotFound("show not found")
            else:
                return _show
        else:
            _shows = db.session.query(Show).filter(_venue.id == venue_id).all()
            return _shows

    @marshal_with(show_response_fields)
    def post(self, venue_id):
        args = show_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        language = args.get("language", None)
        duration = args.get("duration", None)
        rating = args.get("rating", None)
        price = args.get("price", None)
        genre = args.get("genre", None)
        popularity = args.get("popularity", None)
        show_date = args.get("show_date", None)
        show_time = args.get("show_time", None)
        banner_path = args.get("banner_path", None)

        _venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if _venue is None:
            raise NotFound("venue not found")

        _show = Show(
            name=name,
            language=language,
            duration=duration,
            rating=rating,
            price=price,
            genre=genre,
            popularity=popularity,
            show_date=show_date,
            show_time=show_time,
            banner_path=banner_path,
            venue_id=_venue.id,
        )
        db.session.add(_show)
        db.session.commit()

        return _venue, 201

    @marshal_with(show_response_fields)
    def put(self, venue_id, show_id):
        pass

    @marshal_with(show_response_fields)
    def delete(self, venue_id, show_id):
        if venue_id is None:
            raise BadRequest("venue id is missing")
        if show_id is None:
            raise BadRequest("show id is missing")

        show = (
            db.session.query(Show)
            .filter(Show.id == show_id and Show.venue_id == venue_id)
            .first()
        )
        if show is None:
            raise NotFoundError("show does not exist")
        else:
            db.session.delete(Show)
            db.session.commit()


booking_request_parse = reqparse.RequestParser()
booking_request_parse.add_argument("date", type=str, required=True)
booking_request_parse.add_argument("time", type=str, required=True)
booking_request_parse.add_argument("amount", type=str, required=True)

booking_response_fields = {
    "id": fields.Integer,
    "date": fields.String,
    "time": fields.String,
    "amount": fields.String,
}


class BookingAPI(Resource):
    @marshal_with(booking_response_fields)
    def get(self, user_id, show_id, booking_id=None):
        if user_id is None:
            raise BadRequest("user id is not present")
        if show_id is None:
            raise BadRequest("show id is not present")
        if booking_id is not None:
            _booking = (
                db.session.query(Booking)
                .filter(
                    Booking.id == booking_id
                    and Show.id == show_id
                    and User.id == user_id
                )
                .first()
            )
            if _booking is None:
                raise NotFound("booking not found")
        else:
            _bookings = db.session.query(Booking).filter(
                Booking.id == booking_id).all()
            return _bookings

    @marshal_with(booking_response_fields)
    def post(self, user_id, show_id, seats):
        if user_id is None:
            raise BadRequest("user id is not present")
        if show_id is None:
            raise BadRequest("show id is not present")
        if seats is None:
            raise BadRequest("no seats selected")

        _user = db.session.query(User).filter(User.id == user_id).first()
        if _user is None:
            raise NotFound(f"user id {user_id} not found")
        _show = db.session.query(Show).filter(Show.id == show_id).first()
        if _show is None:
            raise NotFound(f"show {show_id} not found")

    def delete(self, user_id, show_id, booking_id):
        pass


def create_admin_user(db):
    admin = User(
        name="Admin",
        email="admin@kino.app",
        username="admin",
        role="admin",
        password=generate_password_hash("iitm"),
        created_on="20-02-2023",
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
