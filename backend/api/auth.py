from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies, set_access_cookies
import re
from datetime import timedelta
from models.User import User

auth_bp = Blueprint('auth', __name__)

email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validaciones básicas
    if not name or not email or not password:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if len(name) < 2 or len(name) > 50:
        return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres"}), 400

    if not email_regex.match(email):
        return jsonify({"error": "Email inválido"}), 400

    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    # Verificar que el email no exista
    if User.find_by_email(email):
        return jsonify({"error": "El email ya está registrado"}), 409

    # Crear usuario
    try:
        user = User(name=name, email=email, password=password)
        user.save()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    user_dict = user.to_dict()
    return jsonify(user_dict), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    if not email_regex.match(email):
        return jsonify({"error": "Email inválido"}), 400

    user = User.find_by_email(email)
    if not user or not user.verify_password(password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # access_token = create_access_token(identity={"id": user.id, "name": user.name, "email": user.email}, expires_delta=timedelta(hours=24))
    # el identity debe ser una cadena
    access_token = create_access_token(identity=user.email, expires_delta=timedelta(hours=24))

    # resp = jsonify({"user": user.to_dict(), "access_token": access_token})

    #set_access_cookies(resp, access_token)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = jsonify({"msg": "Logout exitoso"})
    unset_jwt_cookies(resp)
    return resp, 200
