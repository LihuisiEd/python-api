from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    if db is None:
        return jsonify({"error": "Base de datos no inicializada"}), 500
    
    usuarios_col = db["usuarios"]
    admin_col = db["administradores"]
    clientes_col = db["clientes"]
    data = request.json

    # Validación básica
    if usuarios_col.find_one({"email": data["email"]}):
        return jsonify({"error": "Correo ya registrado"}), 409

    required_fields = ["nombre_usuario", "email", "password", "rol"]
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Campos requeridos"}), 400

    rol = data.get("rol", "cliente")

    # Campos específicos según el rol
    if rol == "admin":
        admin_fields = ["nombres", "apellidos", "telefono"]
        if not all(k in data for k in admin_fields):
            return jsonify({"error": "Faltan campos para registrar admin"}), 400

    elif rol == "cliente":
        cliente_fields = ["nombres", "apellidos", "correo", "telefono", "direccion"]
        if not all(k in data for k in cliente_fields):
            return jsonify({"error": "Faltan campos para registrar cliente"}), 400

    # Insertar en colección de usuarios
    hashed_password = generate_password_hash(data["password"])
    user = {
        "nombre_usuario": data["nombre_usuario"],
        "email": data["email"],
        "password": hashed_password,
        "rol": rol
    }

    result = usuarios_col.insert_one(user)

    # Insertar en colección correspondiente
    if rol == "admin":
        admin_col.insert_one({
            "user_id": result.inserted_id,
            "nombres": data["nombres"],
            "apellidos": data["apellidos"],
            "cargo": data.get("cargo", "Sin definir"),
            "telefono": data["telefono"]
        })
    elif rol == "cliente":
        clientes_col.insert_one({
            "user_id": result.inserted_id,
            "nombres": data["nombres"],
            "apellidos": data["apellidos"],
            "correo": data["correo"],
            "telefono": data["telefono"],
            "direccion": data["direccion"]
        })

    return jsonify({"message": "Usuario registrado correctamente"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    usuarios_col = db["usuarios"]
    data = request.json
    user = usuarios_col.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    claims = {"role": user["rol"]}
    token = create_access_token(identity=str(user["_id"]), additional_claims=claims)

    return jsonify({
        "access_token": token,
        "role": user["rol"],
        "user_id": str(user["_id"]),
        "nombre_usuario": user["nombre_usuario"]
    }), 200
