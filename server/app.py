#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

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
            return make_response([scientist.to_dict() for scientist in Scientist.query], 200)
        except Exception as e:
            return make_response(str(e), 400)
    
    def post(self):
        try:
            #! extract the data out of the request
            data = request.get_json()
            #! instantiate a new scientist object
            #* It's at this point that @validates validations kick in!!!
            new_scientist = Scientist(**data)
            #! start the process to persist the scientist
            db.session.add(new_scientist)
            #* It's at this point that db constraints kick in!!!
            db.session.commit()
            return new_scientist.to_dict(rules=("missions",)), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)

class ScientistById(Resource):
    def patch(self, id):
        try:
            #! Try to find the scientist by the id given
            if scientist := db.session.get(Scientist, id):
                #! retrieve the data out of the request
                data = request.get_json()
                #! patch the object with mass assignment
                for attr, value in data.items():
                    #* It's at this point that @validates validations kick in!!!
                    setattr(scientist, attr, value)
                #* It's at this point that db constraints kick in!!!
                db.session.commit()
                return scientist.to_dict(rules=("missions",)), 202
            return {"error": "Scientist not found"}, 404
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)
    
    def delete(self, id):
        try:
            if scientist := db.session.get(Scientist, id):
                db.session.delete(scientist)
                db.session.commit()
                return {}, 204
            return {"error": "Scientist not found"}, 404
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 422)

api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistById, "/scientists/<int:id>")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
