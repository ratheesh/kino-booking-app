from flask import Blueprint
from flask_restful import Resource

# from .db import db
# from flask_sqlalchemy import SQLAlchemy

api = Blueprint('api', __name__)

hapi = None


class Venue(Resource):
    def get(self):
        return {"001": "Bengaluru"}

    # def get(self, venue_id):
    #     return {"001": "Bengaluru"}

    def put(self, venue_id):
        pass

    def post(self, venue_id):
        pass

    def delete(self, venue_id):
        pass


class Show(Resource):
    def get(self):
        return {"001": "Avatar"}

    def put(self, venue_id):
        pass

    def post(self, venue_id):
        pass

    def delete(self, venue_id):
        pass


# End of File
