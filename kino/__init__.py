import os

from flask import Blueprint, Flask, url_for
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from .api import Show, Venue
from .db import db

DB_NAME = 'kino.db'
app = None


def create_app():
    global hapi
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = 'iitm-mad1-projeckt'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        basedir, 'kino.sqlite3'
    )

    hapi = Api(app)
    db.init_app(app)
    app.app_context().push()

    from .api import api
    from .views import views

    app.register_blueprint(views, url_prefix='/view')
    app.register_blueprint(api, url_prefix='/api')

    hapi.add_resource(Venue, '/api/venue', '/api/venue<string:venue_id>')
    hapi.add_resource(Show, '/api/show', '/api/show/<string:show_id>')

    return app


# app = create_app()


# if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0")

# End of File
