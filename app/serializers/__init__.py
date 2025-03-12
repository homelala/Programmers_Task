from functools import partial
from flask_apispec import marshal_with
from marshmallow import Schema

marshal_empty = partial(marshal_with, Schema)
