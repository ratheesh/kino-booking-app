import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .api import ShowAPI, UserAPI, VenueAPI, create_admin_user
from .db import db

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

    from .admin import admin
    from .api import api
    from .auth import auth
    from .frontend import frontend

    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(frontend, url_prefix="/")

    hapi.add_resource(UserAPI, "/api/user", "/api/user/<int:user_id>")
    hapi.add_resource(VenueAPI, "/api/venue", "/api/venue/<string:venue_id>")
    hapi.add_resource(ShowAPI, "/api/show", "/api/show/<string:show_id>")

    return app


# app = create_app()


# if __name__ == "__main__":
# app.run(debug=True, host="0.0.0.0")

# End of File
