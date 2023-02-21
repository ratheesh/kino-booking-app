from flask import Blueprint, make_response
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.exceptions import HTTPException

from .db import Show, User, Venue, db

# from flask_sqlalchemy import SQLAlchemy

api = Blueprint("api", __name__)

hapi = None


class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("", status_code)


user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("name", type=ascii)
user_request_parse.add_argument("username", type=ascii)
user_request_parse.add_argument("password", type=ascii)
user_request_parse.add_argument("email", type=ascii)
user_request_parse.add_argument("created_on", type=ascii)

user_response_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "username": fields.String,
    "password": fields.String,
    "email": fields.String,
    "created_on": fields.String,
}


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
        password = args.get("password", None)
        email = args.get("email", None)
        created_on = args.get("created_on", None)

        new_user = User(
            name=name,
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


# End of File
