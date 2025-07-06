from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required
from utils.auth import role_required
from werkzeug.security import generate_password_hash, check_password_hash

usuarios_bp = Blueprint("usuarios", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todos los usuarios (solo admin)
@usuarios_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all():
    col = db["usuarios"]
    usuarios = list(col.find())
    for u in usuarios:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
    return jsonify(usuarios), 200

# 🔹 POST: crear nuevo usuario (solo admin)
@usuarios_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin")
def create():
    col = db["usuarios"]
    data = request.json
    required = ("nombre_usuario", "email", "password", "rol")
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Verifica unicidad de email o nombre de usuario
    if col.find_one({"$or": [{"email": data["email"]}, {"nombre_usuario": data["nombre_usuario"]}]}):
        return jsonify({"error": "Usuario o email ya registrado"}), 409

    user = {
        "nombre_usuario": data["nombre_usuario"],
        "email": data["email"],
        "rol": data["rol"],
        "password": generate_password_hash(data["password"])
    }

    result = col.insert_one(user)
    new = col.find_one({"_id": result.inserted_id})
    new["_id"] = str(new["_id"])
    new.pop("password", None)
    return jsonify(new), 201

# 🔹 GET: obtener usuario por ID (solo admin)
@usuarios_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_one(id):
    col = db["usuarios"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    user = col.find_one({"_id": ObjectId(id)})
    if not user:
        return jsonify({"error": "No encontrado"}), 404

    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return jsonify(user), 200

# 🔹 PUT: actualizar usuario (solo admin)
@usuarios_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["usuarios"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    data = request.json

    if "password" in data:
        data["password"] = generate_password_hash(data["password"]) 

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    updated.pop("password", None)
    return jsonify(updated), 200

# 🔹 DELETE: eliminar usuario (solo admin)
@usuarios_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["usuarios"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    return jsonify({"message": "Usuario eliminado correctamente"}), 200
