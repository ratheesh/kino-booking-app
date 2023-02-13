import os

from flask import Blueprint, Flask, url_for

# from application.controllers import *
from application.database import db

app = None


def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "iitm-mad1-projeckt"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "kino.sqlite3"
    )

    db.init_app(app)
    app.app_context().push()

    from .application.views import views

    app.register_blueprint(views, url_prefix="/view")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

# End of File
