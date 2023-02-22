from flask import Blueprint, make_response
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from .db import Show, User, Venue, db

# from flask_sqlalchemy import SQLAlchemy

auth = HTTPBasicAuth()
api = Blueprint("api", __name__)

hapi = None


class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("", status_code)


user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("name")
user_request_parse.add_argument("username")
user_request_parse.add_argument("password")
user_request_parse.add_argument("email")
user_request_parse.add_argument("created_on")

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
        # return '{"hello": "world"}'

        if user_id is not None:
            user_details = db.session.query(
                User).filter(User.id == user_id).first()

            if user_details:
                return user_details
            else:
                raise NotFoundError(status_code=404)
        else:  # send details of all users
            users = db.session.query(User).all()
            print(users)
            return users

    @marshal_with(user_response_fields)
    def post(self):
        args = user_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        username = args.get("username", None)
        password = generate_password_hash(args.get("password", None))
        email = args.get("email", None)
        created_on = args.get("created_on", None)

        new_user = User(
            name=name,
            role="user",
            username=username,
            password=password,
            email=email,
            created_on=created_on,
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user, 201

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


venue_request_parse = reqparse.RequestParser()
venue_request_parse.add_argument("name", type=ascii)
venue_request_parse.add_argument("city", type=ascii)

venue_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "city": fields.String,
}


class VenueAPI(Resource):
    @marshal_with(venue_response_fields)
    @auth.login_required(role="admin")
    def get(self, venue_id=None):
        if venue_id is not None:
            venue_details = db.session.query(
                Venue).filter(Venue.id == venue_id).first()

            if venue_details:
                return venue_details
            else:
                raise NotFoundError(status_code=404)
        else:  # send details of all users
            venues = db.session.query(Venue).all()
            print(Venue)
            return venues

    @marshal_with(venue_response_fields)
    def post(self):
        args = venue_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        city = args.get("city", None)

        new_venue = Venue(
            name=name,
            city=city,
        )
        db.session.add(new_venue)
        db.session.commit()

        return new_venue, 201

    def put(self, venue_id):
        pass

    def delete(self, venue_id):
        pass


class ShowAPI(Resource):
    def get(self):
        return {"001": "Avatar"}

    def put(self, venue_id):
        pass

    def post(self, venue_id):
        pass

    def delete(self, venue_id):
        pass


def create_admin_user(db):
    admin = User(
            name="Admin",
            email="admin@kino.app",
            username="admin",
            role="admin",
            password=generate_password_hash("iitm"),
            created_on="20-02-2023"
            )
    db.session.add(admin)
    db.session.commit()


# End of File
