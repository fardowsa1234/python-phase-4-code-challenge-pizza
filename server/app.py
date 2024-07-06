#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.serialize() for restaurant in restaurants])
    except Exception as e:
        return make_response(str(e), 500)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.serialize())
        else:
            return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    except Exception as e:
        return make_response(str(e), 500)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    except Exception as e:
        return make_response(str(e), 500)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        return jsonify([pizza.serialize() for pizza in pizzas])
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        price = data.get('price')
        if not (1 <= price <= 30):
            return make_response(jsonify({'error': 'Price must be between 1 and 30'}), 400)
        
        restaurant_id = data.get('restaurant_id')
        pizza_id = data.get('pizza_id')

        if not restaurant_id or not pizza_id:
            return make_response(jsonify({'error': 'Missing restaurant_id or pizza_id'}), 400)

        pizza = Pizza.query.get(pizza_id)
        if not pizza:
            return make_response(jsonify({'error': 'Pizza not found'}), 404)

        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return make_response(jsonify({'error': 'Restaurant not found'}), 404)

        restaurant_pizza = RestaurantPizza(
            restaurant_id=restaurant_id,
            pizza_id=pizza_id,
            price=price
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.serialize()), 201
    except KeyError as ke:
        return make_response(jsonify({'error': f'Missing field {str(ke)}'}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
