import os

from flask import Flask
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_restful import Api

from .api import BookingAPI, ShowAPI, UserAPI, VenueAPI, api
from .controller import controller
from .db import User, create_admin_user, db, populate_tags

DB_FILE = "kino.sqlite3"
app = None


def create_app():
    global hapi
    basedir = os.path.abspath(os.path.dirname(__file__))

    db_file = "sqlite:///" + os.path.join(basedir, DB_FILE)
    app = Flask(__name__, template_folder="templates")

    app.debug = True

    app.config["SECRET_KEY"] = "kino-booking-app"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_file
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["IMG_FOLDER"] = basedir + "./static/img"

    CORS(app)
    hapi = Api(app)
    db.init_app(app)
    app.app_context().push()

    dbfile = os.path.join(basedir, DB_FILE)
    if not os.path.exists(dbfile):
        print("db file: ", dbfile)
        print("==== DB FILE DOES NOT EXIST, CREATING ONE =====")
        db.create_all()
        print("==== CREATING ADMIN USER =====")
        create_admin_user(db)
        print("==== Populating tags =====")
        populate_tags(db)

    login_manager = LoginManager(app)
    login_manager.login_view = "controller.login"
    login_manager.login_message_category="success"
    login_manager.needs_refresh_message_category="warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(controller, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")

    hapi.add_resource(
        UserAPI,
        "/api/user",
        "/api/user/<username>",
    )
    hapi.add_resource(VenueAPI, "/api/venue", "/api/venue/<int:venue_id>")
    hapi.add_resource(ShowAPI, "/api/<int:venue_id>/show", "/api/<int:venue_id>/show/<int:show_id>"
    )

    return app


# app = create_app()


# if __name__ == "__main__":
# app.run(debug=True, host="0.0.0.0")

# End of File
