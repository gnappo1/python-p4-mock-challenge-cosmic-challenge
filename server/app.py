#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
from werkzeug.exceptions import NotFound

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        try:
            return [scientist.to_dict() for scientist in Scientist.query], 200
        except Exception as e:
            return {"error":  str(e)}, 400

api.add_resource(Scientists, "/scientists")
class Planets(Resource):
    def get(self):
        try:
            return [planet.to_dict() for planet in Planet.query], 200
        except Exception as e:
            return {"error":  str(e)}, 400

api.add_resource(Planets, "/planets")

class ScientistById(Resource):
    def patch(self, id):
        try:
            scientist = Scientist.query.get_or_404(id, "Scientist not found")
            data = request.json
            for k, v in data.items():
                if hasattr(scientist, k):
                    setattr(scientist, k, v)
            db.session.commit()
            return scientist.to_dict(), 202
        except Exception as e:
            return {"error": str(e)}, 400

    def delete(self, id):
        try:
            scientist = Scientist.query.get_or_404(id, "Scientist not found")
            db.session.delete(scientist)
            db.session.commit()
            return "", 204
        except NotFound as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 400

api.add_resource(ScientistById, "/scientists/<int:id>")

if __name__ == '__main__':
    app.run(port=5555)
