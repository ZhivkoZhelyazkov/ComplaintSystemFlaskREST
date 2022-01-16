from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from psycopg2.errorcodes import UNIQUE_VIOLATION
from werkzeug.exceptions import BadRequest, InternalServerError

from flask_cors import CORS
from config import DevApplication
from db import db
from resources.routes import routes

app = Flask(__name__)
app.config.from_object(DevApplication)
db.init_app(app)

migrate = Migrate(app, db)
CORS(app)
api = Api(app)

[api.add_resource(*r) for r in routes]


@app.after_request
def conclude_request(response):
    try:
        db.session.commit()
    except Exception as ex:
        if ex.orig.pgcode == UNIQUE_VIOLATION:
            raise BadRequest("Please login")
        else:
            raise InternalServerError("Server is unavailable. Please try again later.")
    return response


if __name__ == "__main__":
    app.run()
    # app.run(host='127.0.0.1', port=8000, debug=True)
