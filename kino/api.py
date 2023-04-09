from datetime import datetime

from flask import Blueprint, make_response
from flask_restful import (NotFound, Resource, fields, marshal_with, reqparse,
                           request)
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from kino.controller import internal_server_error

from .db import Booking, Show, Tag, User, Venue, db
import json

api = Blueprint("api", __name__)

class BadRequest(HTTPException):
    def __init__(self,msg, error_code=None):
        self.response = make_response(msg, 400)

class UnAuthorizedAccess(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 403)

class NotFoundError(HTTPException):
    def __init__(self,msg, error_code=None):
        self.response = make_response(msg, 404)

class InternalServerError(HTTPException):
    def __init__(self, msg=""):
        self.response = make_response(msg, 500)


user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("name", type=str)
user_request_parse.add_argument("username", type=str)
user_request_parse.add_argument("password", type=str)
# user_request_parse.add_argument("image", type=str)

user_response_fields = {
    "id": fields.Integer,
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
            raise BadRequest("Name not provided")
        if username is None:
            raise BadRequest("Username not provided")
        if password is None:
            raise BadRequest("Password not provided")
        if len(password) < 4:
            raise BadRequest("Password length is less than 4 chars")

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
        if user is None:
            raise InternalServerError(msg="Error in creating User")
        else:
            try:
                db.session.add(user)
                db.session.commit()
            except:
                raise InternalServerError(msg="Error in creating User")

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
                if user.username == "admin":
                    raise UnAuthorizedAccess(msg="Admin profile can not modified")

                user.name = name
                user.password = password
                user.updated_timestamp=datetime.now()
            else:
                raise NotFoundError(msg="User not found")

            try:
                db.session.add(user)
                db.session.commit()
            except:
                raise InternalServerError(msg="Error in updating User")

            return user,200

    def delete(self, username):
        if username is None:
            raise BadRequest("User name is missing")
        else:
            user = User.query.filter_by(username=username).first()
            if user is None:
                raise NotFoundError(msg="User not found")
            try:
                db.session.delete(user)
                db.session.commit()
            except:
                raise InternalServerError(msg="Error deleting User")

        return "User deleted successfully",200

################################################## VENUE ###############################################################

venue_request_parse = reqparse.RequestParser()
venue_request_parse.add_argument("name", type=str, required=True)
venue_request_parse.add_argument("place", type=str, required=True)

venue_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "place": fields.String,
    "venue_img": fields.String,
    "created_timestamp": fields.DateTime,
    "updated_timestamp": fields.DateTime,
}

class VenueAPI(Resource):
    @marshal_with(venue_response_fields)
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
        venue_img="default.jpg"

        venue = Venue(name=name,
                       place=place,
                       venue_img=venue_img,
                       created_timestamp=datetime.now(),
                       updated_timestamp=datetime.now()
                       )
        if venue is None:
            raise InternalServerError(msg="Error creating Venue")

        try:
            db.session.add(venue)
            db.session.commit()
        except:
            raise InternalServerError(msg="Error creating Venue")

        return venue, 201

    @marshal_with(venue_response_fields)
    def put(self, venue_id):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        place = args.get("place", None)
        if name is None:
            raise BadRequest("Venue Name is missing")
        if place is None:
            raise BadRequest("Venue Place is missing")

        venue =  Venue.query.filter_by(id=venue_id).first()
        if venue:
            venue.name = name
            venue.place = place
            venue.updated_timestamp=datetime.now()
        else:
            raise NotFoundError("Venue not found")

        try:
            db.session.add(venue)
            db.session.commit()
        except:
            raise InternalServerError(msg="Error updating Venue")
        return venue, 200

    def delete(self, venue_id):
        if venue_id is None:
            raise BadRequest("Venue ID is missing")
        else:
            venue = Venue.query.filter_by(id=venue_id).first()
            if venue is None:
                raise NotFoundError("Venue not found")
            else:
                try:
                    db.session.delete(venue)
                    db.session.commit()
                except:
                    raise InternalServerError(msg="Error deleting Venue")
            return "Venue deleted successfully", 200

def valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M")

show_request_parse = reqparse.RequestParser()
show_request_parse.add_argument("title", type=str, required=True)
show_request_parse.add_argument("language", type=str, required=True)
show_request_parse.add_argument("duration", type=int, required=True)
show_request_parse.add_argument("price", type=int, required=True)
show_request_parse.add_argument("rating", type=float, required=True)
show_request_parse.add_argument("show_time", type=valid_date, required=True)
show_request_parse.add_argument("n_rows", type=int, required=True)
show_request_parse.add_argument("n_seats", type=int, required=True)
# show_request_parse.add_argument("venue_id", type=int, required=True)


show_response_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "language": fields.String,
    "duration": fields.Integer,
    "price": fields.Integer,
    "rating": fields.Float,
    "show_time": fields.DateTime,
    "n_rows": fields.Integer,
    "n_seats": fields.Integer,
    "show_img": fields.String,
    "created_timestamp": fields.DateTime,
    "updated_timestamp": fields.DateTime,
    "venue_id": fields.Integer,
}


class ShowAPI(Resource):
    @marshal_with(show_response_fields)
    def get(self, venue_id, show_id=None):
        if venue_id is None:
            raise BadRequest("Venue ID is null")

        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise BadRequest("Venue not found")

        if show_id is not None:
            show = (
                db.session.query(Show)
                .filter(Show.id == show_id, venue.id == venue_id)
                .first()
            )
            if show is None:
                raise NotFound("Show not found")
            else:
                return show,200
        else:
            shows = db.session.query(Show).filter(venue.id == venue_id).all()
            return shows,200

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
        show_img="default.jpg"

        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise NotFound("Venue not found")

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
            created_timestamp=datetime.now(),
            updated_timestamp=datetime.now()
        )
        if show is None:
            raise InternalServerError(msg="Error creating Show")

        try:
            db.session.add(show)
            db.session.commit()
        except:
            raise InternalServerError(msg="Error creating Show")

        return show, 201

    @marshal_with(show_response_fields)
    def put(self, venue_id, show_id):
        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        if venue is None:
            raise NotFound("Venue not found")

        show =  Show.query.filter_by(id=show_id, venue_id=venue.id).first()
        if show is not None:
            args = show_request_parse.parse_args(strict=True)
            title = args.get("title", None)
            language = args.get("language", None)
            duration = args.get("duration", None)
            price = args.get("price", None)
            rating = args.get("rating", None)
            show_time = args.get("show_time", None)
            n_rows = args.get("n_rows", None)
            n_seats = args.get("n_seats", None)

            show.title=title
            show.language=language
            show.duration=duration
            show.price=price
            show.rating=rating
            show.show_time=show_time
            show.n_rows=n_rows
            show.n_seats=n_seats
            show.venue_id=venue.id
            show.updated_timestamp=datetime.now()
        else:
            raise NotFoundError("Show not found")

        try:
            db.session.add(show)
            db.session.commit()
        except:
            raise InternalServerError(msg="Error updating show")

        return show, 200

    def delete(self, venue_id, show_id):
        if venue_id is None:
            raise BadRequest("Venue id is missing")
        if show_id is None:
            raise BadRequest("Show id is missing")

        show = (
            db.session.query(Show)
            .filter(Show.id == show_id, Show.venue_id == venue_id)
            .first()
        )
        if show is None:
            raise NotFoundError("Show does not exist")
        else:
            try:
                db.session.delete(show)
                db.session.commit()
            except:
                raise InternalServerError(msg="Error deleting Show")

            return "Show deleted Successfully", 200

# End of File
