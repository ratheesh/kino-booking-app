from datetime import datetime

from flask import Blueprint, make_response
from flask_restful import (NotFound, Resource, fields, marshal_with, reqparse,
                           request)
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from kino.controller import internal_server_error

from .db import Booking, Show, Tag, User, Venue, db

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

class AlreadyExistsError(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 403)

class InternalServerError(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 500)



user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("name", type=str)
user_request_parse.add_argument("username", type=str)
user_request_parse.add_argument("password", type=str)
user_request_parse.add_argument("image", type=str)

user_response_fields = {
    "name": fields.String,
    "username": fields.String,
    "password": fields.String,
    "role":fields.String,
    "profile_img": fields.String,
    "created_timestamp":fields.DateTime,
    "updated_timestamp":fields.DateTime,
}


class UserAPI(Resource):
    @marshal_with(user_response_fields)
    def get(self, username=None):
        if username is not None:
            user = User.query.filter_by(username=username).first()
            if user:
                return user,200
            else:
                raise NotFoundError(msg="User not found")
        else:
            users=User.query.all()
            return users,200

    @marshal_with(user_response_fields)
    def post(self):
        args = user_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        username = args.get("username", None)
        password = args.get("password", None)

        # if args is None or name is None or username is None or password is None:
        if name is None:
            raise BadRequest("name not provided")
        if username is None:
            raise BadRequest("username not provided")
        if password is None:
            raise BadRequest("password not provided")
        if len(password) < 4:
            raise BadRequest("password length is less than 4 chars")

        # check if the user already exists based on username
        user = User.query.filter_by(username=username).first()
        if user is not None:
            print("=== user already exists === ")
            raise BadRequest("user already exists")

        user = User(
            name=name,
            username=username,
            password=generate_password_hash(password),
            role="user",
            profile_img="default.jpg",
            created_timestamp=datetime.now(),
            updated_timestamp=datetime.now(),
        )
        db.session.add(user)
        db.session.commit()

        return user, 201

    @marshal_with(user_response_fields)
    def put(self, username):
        if username is None:
            raise BadRequest("username not given")
        else:
            args = user_request_parse.parse_args(strict=True)
            name = args.get("name", None)
            password = generate_password_hash(args.get("password", None))

            user = User.query.filter_by(username=username).first()
            if user is not None:
                user.name = name
                user.password = password
                updated_timestamp=datetime.now(),
            else:
                raise NotFoundError("user not found")

            db.session.add(user)
            db.session.commit()
            return user

    def delete(self, username):
        if username is None:
            raise BadRequest("user name is missing")
        else:
            user = User.query.filter_by(username=username).first()
            if user is None:
                raise NotFoundError(msg="User not found")
            db.session.delete(user)
            db.session.commit()
        return "User deleted successfully",200

################################################## VENUE ###############################################################

venue_request_parse = reqparse.RequestParser()
venue_request_parse.add_argument("name", type=str, required=True)
venue_request_parse.add_argument("place", type=str, required=True)

venue_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "place": fields.String,
    "created_time": fields.String,
    "updated_time": fields.String,
}


class VenueAPI(Resource):
    @marshal_with(venue_response_fields)
    # @auth.login_required(role="admin")
    def get(self, venue_id=None):
        if venue_id is not None:
            venue = Venue.query.filter_by(id=venue_id).first()
            if venue:
                return venue,200
            else:
                raise NotFoundError(msg="Venue not found")
        else:
            venues = Venue.query.all()
            return venues,200

    @marshal_with(venue_response_fields)
    def post(self):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        place = args.get("place", None)

        venue = Venue( name=name, place=place)
        if venue is None:
            raise InternalServerError(msg="Error creating Venue")
        db.session.add(venue)
        db.session.commit()
        return venue, 201

    @marshal_with(venue_response_fields)
    def put(self, venue_id):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        place = args.get("place", None)
        if name is None:
            raise BadRequest("name is missing")
        if place is None:
            raise BadRequest("place is missing")

        venue =  Venue.query.filter_by(id=venue_id).first()
        if venue:
            venue.name = name
            venue.place = place
        else:
            raise NotFoundError("Venue not found")

        db.session.add(venue)
        db.session.commit()
        return "Venue details updated", 200

    def delete(self, venue_id):
        if venue_id is None:
            raise BadRequest("id is missing")
        else:
            venue = Venue.query.filter_by(id=venue_id).first()
            if venue is None:
                raise NotFoundError("Venue not found")
            else:
                db.session.delete(venue)
                db.session.commit()
                return "Venue deleted successfully", 200


show_request_parse = reqparse.RequestParser()
show_request_parse.add_argument("title", type=str)
show_request_parse.add_argument("language", type=str)
show_request_parse.add_argument("duration", type=int)
show_request_parse.add_argument("price", type=int)
show_request_parse.add_argument("rating", type=str)
show_request_parse.add_argument("show_time", type=datetime)
show_request_parse.add_argument("n_rows", type=int)
show_request_parse.add_argument("n_seats", type=int)
show_request_parse.add_argument("show_img", type=str)


show_response_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "language": fields.String,
    "duration": fields.Integer,
    "price": fields.Integer,
    "rating": fields.String,
    "show_time": fields.DateTime,
    "n_rows": fields.Integer,
    "n_seats": fields.Integer,
    "show_img": fields.String,
    "created_timestamp": fields.DateTime,
    "updated_timestamp": fields.DateTime,
}


class ShowAPI(Resource):
    @marshal_with(show_response_fields)
    def get(self, venue_id, show_id=None):
        if venue_id is None:
            raise BadRequest("venue id null")

        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise BadRequest("venue not found")

        if show_id is not None:
            show = (
                db.session.query(Show)
                .filter(Show.id == show_id and venue.id == venue_id)
                .first()
            )
            if show is None:
                raise NotFound("show not found")
            else:
                return show
        else:
            shows = db.session.query(Show).filter(venue.id == venue_id).all()
            return shows

    @marshal_with(show_response_fields)
    def post(self, venue_id):
        args = show_request_parse.parse_args(strict=True)
        title = args.get("title", None)
        language = args.get("language", None)
        duration = args.get("duration", None)
        price = args.get("price", None)
        rating = args.get("rating", None)
        show_time = args.get("show_time", None)
        n_rows = args.get("n_rows", None)
        n_seats = args.get("n_seats", None)
        show_img = args.get("show_img", None)

        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise NotFound("venue not found")

        show = Show(
            title=title,
            language=language,
            duration=duration,
            price=price,
            rating=rating,
            show_time=show_time,
            n_rows=n_rows,
            n_seats=n_seats,
            show_img=show_img,
            venue_id=venue.id,
        )
        db.session.add(show)
        db.session.commit()

        return show, 201

    @marshal_with(show_response_fields)
    def put(self, venue_id, show_id):
        args = show_request_parse.parse_args(strict=True)
        title = args.get("title", None)
        language = args.get("language", None)
        duration = args.get("duration", None)
        rating = args.get("rating", None)
        price = args.get("price", None)
        genre = args.get("genre", None)
        show_date = args.get("show_date", None)
        show_time = args.get("show_time", None)
        banner_path = args.get("banner_path", None)

        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise NotFound("venue not found")

        show =  Show.query.filter_by(id=show_id, venue_id=venue.id).first()
        if show:
            show.title=title,
            show.language=language,
            show.duration=duration,
            show.rating=rating,
            show.price=price,
            show.genre=genre,
            show.show_date=show_date,
            show.show_time=show_time,
            show.show_img=banner_path,
            show.venue_id=venue.id,
            show.updated_timestamp=datetime.now(),
        else:
            raise NotFoundError("Show not found")

        db.session.add(venue)
        db.session.commit()
        return "Venue details updated", 200

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

# End of File
