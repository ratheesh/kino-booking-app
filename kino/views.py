# from flask import Flask, request
from flask import Blueprint
# from flask import current_app as app


views = Blueprint('controller', __name__)


@views.route('/', methods=['GET', 'POST'])
def venue():
    return '<h1> Venu Management </h1>'

# End of File
