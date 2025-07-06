from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required
from utils.auth import role_required

admin_bp = Blueprint("administradores", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todos los administradores
@admin_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all():
    col = db["administradores"]
    items = list(col.find())
    for item in items:
        item["_id"] = str(item["_id"])
        item["user_id"] = str(item["user_id"])
    return jsonify(items), 200

# 🔹 POST: crear un nuevo administrador
@admin_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin")
def create():
    col = db["administradores"]
    data = request.json
    required_fields = ["user_id", "nombres", "apellidos", "cargo", "telefono"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if not is_valid_objectid(data["user_id"]):
        return jsonify({"error": "ID de usuario inválido"}), 400

    admin = {
        "user_id": ObjectId(data["user_id"]),
        "nombres": data["nombres"],
        "apellidos": data["apellidos"],
        "cargo": data["cargo"],
        "telefono": data["telefono"]
    }

    result = col.insert_one(admin)
    admin["_id"] = str(result.inserted_id)
    admin["user_id"] = str(admin["user_id"])
    return jsonify(admin), 201

# 🔹 GET: obtener un administrador por ID
@admin_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_one(id):
    col = db["administradores"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    item = col.find_one({"_id": ObjectId(id)})
    if not item:
        return jsonify({"error": "No encontrado"}), 404
    item["_id"] = str(item["_id"])
    item["user_id"] = str(item["user_id"])
    return jsonify(item), 200

# 🔹 PUT: actualizar un administrador
@admin_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["administradores"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    data = request.json

    if "user_id" in data:
        if not is_valid_objectid(data["user_id"]):
            return jsonify({"error": "ID de usuario inválido"}), 400
        data["user_id"] = ObjectId(data["user_id"])

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    updated["user_id"] = str(updated["user_id"])
    return jsonify(updated), 200

# 🔹 DELETE: eliminar un administrador
@admin_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["administradores"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify({"message": "Administrador eliminado correctamente"}), 200
