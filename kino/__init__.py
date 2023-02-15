import os

from flask import Blueprint, Flask, url_for
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from .api import ShowAPI, UserAPI, VenueAPI
from .db import db

DB_NAME = "kino.db"
app = None


def create_app():
    global hapi
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "iitm-mad1-projeckt"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "kino.sqlite3"
    )

    hapi = Api(app)
    db.init_app(app)
    app.app_context().push()

    # db.create_all()

    from .api import api
    from .views import views
    from .auth import auth

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(views, url_prefix="/view")

    hapi.add_resource(UserAPI, "/api/user", "/api/user/<int:user_id>")
    hapi.add_resource(VenueAPI, "/api/venue", "/api/venue/<string:venue_id>")
    hapi.add_resource(ShowAPI, "/api/show", "/api/show/<string:show_id>")

    return app


# app = create_app()


# if __name__ == "__main__":
# app.run(debug=True, host="0.0.0.0")

# End of File
