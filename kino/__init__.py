import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .api import BookingAPI, ShowAPI, UserAPI, VenueAPI
from .db import create_admin_user, db, populate_tags

DB_FILE = "kino.sqlite3"
app = None


def create_app():
    global hapi
    basedir = os.path.abspath(os.path.dirname(__file__))

    db_file = "sqlite:///" + os.path.join(basedir, DB_FILE)
    app = Flask(__name__, template_folder="templates")

    app.config["SECRET_KEY"] = "iitm-mad1-projeckt"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_file

    CORS(app)
    hapi = Api(app)
    db.init_app(app)
    app.app_context().push()

    dbfile = os.path.join(basedir, DB_FILE)
    if not os.path.exists(dbfile):
        print("db file: ", dbfile)
        print("==== DB FILE DOES NOT EXIST, CREATING TABLES =====")
        db.create_all()
        print("==== CREATING ADMIN USER =====")
        create_admin_user(db)
        print("==== Populating tags =====")
        populate_tags(db)

    from .admin import admin
    from .api import api
    from .auth import auth
    from .controller import controller

    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(controller, url_prefix="/")

    hapi.add_resource(
        UserAPI,
        "/api/user",
        "/api/user/<username>",
        "/api/user/<username>/bookings",
    )
    hapi.add_resource(VenueAPI, "/api/venue", "/api/venue/<int:venue_id>")
    hapi.add_resource(
        ShowAPI, "/api/<int:venue_id>/show", "/api/<int:venue_id>/show/<int:show_id>"
    )
    hapi.add_resource(
        BookingAPI,
        "/api/<int:show_id>/book",
    )

    return app


# app = create_app()


# if __name__ == "__main__":
# app.run(debug=True, host="0.0.0.0")

# End of File
