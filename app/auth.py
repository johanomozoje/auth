from flask import Blueprint, request, jsonify
from app import mongo
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Missing JSON in requst"}), 400

        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password:
            return jsonify({"msg": "Missing email or password"}), 401

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return jsonify({"msg": "User already exists"}), 409

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "name": name
        }
        result = mongo.db.users.insert_one(user_data)

        access_token = create_access_token(
            identity=str(
                result.inserted_id), expires_delta=timedelta(days=7)
        )
        return jsonify({"msg": "User created successfully", "access_token": access_token}), 201

    except Exception as e:
        return jsonify({"msg": "Error during signup", "error": str(e)}), 500
