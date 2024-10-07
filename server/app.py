#!/usr/bin/env python3

from flask import Flask, request, make_response, json
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Route to get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    try:
        heroes = Hero.query.all()
        response_data = [hero.to_dict() for hero in heroes]
        response = make_response(response_data)
        response.mimetype = 'application/json'
        return response
    except Exception as e:
        error_response = make_response({"error": str(e)})
        error_response.mimetype = 'application/json'
        error_response.status_code = 500
        return error_response

# Route to get a specific hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        hero_data = hero.to_dict()
        hero_data['powers'] = [{'id': hp.power_id, 'name': hp.power.name} for hp in hero.hero_powers]
        return make_response(json.dumps(hero_data), 200)
    else:
        return make_response(json.dumps({"error": "Hero not found"}), 404)

# Route to get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    response_data = [power.to_dict() for power in powers]
    return make_response(json.dumps(response_data), 200)

# Route to get a specific power by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power:
        return make_response(json.dumps(power.to_dict()), 200)
    else:
        return make_response(json.dumps({"error": "Power not found"}), 404)

# Route to update an existing power
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power:
        data = request.get_json()
        if 'description' in data:
            power.description = data['description']
            try:
                db.session.commit()
                return make_response(json.dumps(power.to_dict()), 200)
            except Exception as e:
                return make_response(json.dumps({"errors": ["validation errors"]}), 400)
    else:
        return make_response(json.dumps({"error": "Power not found"}), 404)

# Route to create a new HeroPower
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    try:
        new_hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
        
        return make_response(json.dumps({
            "id": new_hero_power.id,
            "hero_id": new_hero_power.hero_id,
            "power_id": new_hero_power.power_id,
            "strength": new_hero_power.strength
        }), 201)
        
    except Exception as e:
        return make_response(json.dumps({"errors": ["validation errors"]}), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
 