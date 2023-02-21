from flask import Blueprint, make_response
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.exceptions import HTTPException

from .db import User, db

# from flask_sqlalchemy import SQLAlchemy

api = Blueprint("api", __name__)

hapi = None


class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("", status_code)


user_request_parse = reqparse.RequestParser()
user_request_parse.add_argument("email")
user_request_parse.add_argument("dob")
user_request_parse.add_argument("first_name")
user_request_parse.add_argument("last_name")
user_request_parse.add_argument("username")
user_request_parse.add_argument("password")
user_request_parse.add_argument("recovery_key")
user_request_parse.add_argument("created_on")

user_response_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "dob": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "username": fields.String,
    "password": fields.String,
    "recovery_key": fields.String,
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
        args = user_request_parse.parse_args()
        email = args.get("email", None)
        dob = args.get("dob", None)
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        username = args.get("username", None)
        passwd = args.get("password", None)
        recovery_key = args.get("recovery_key", None)
        created_on = args.get("created_on", None)

        new_user = User(
            email=email,
            dob=dob,
            first_name=first_name,
            last_name=last_name,
            username=username,
            passwd=passwd,
            recovery_key=recovery_key,
            created_on=created_on,
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user, 201

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class VenueAPI(Resource):
    def get(self):
        return {"001": "Bengaluru"}

    # def get(self, venue_id):
    #     return {"001": "Bengaluru"}

    def post(self, venue_id):
        pass

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
