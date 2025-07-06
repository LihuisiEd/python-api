from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required
from utils.auth import role_required

categorias_bp = Blueprint("categorias", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todas las categorías (público)
@categorias_bp.route("/", methods=["GET"])
def get_all():
    col = db["categorias"]
    items = list(col.find())
    for item in items:
        item["_id"] = str(item["_id"])
    return jsonify(items), 200

# 🔹 POST: crear una nueva categoría (admin)
@categorias_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin")
def create():
    col = db["categorias"]
    data = request.json
    required_fields = ["nombre", "descripcion"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    categoria = {
        "nombre": data["nombre"],
        "descripcion": data["descripcion"]
    }

    result = col.insert_one(categoria)
    categoria["_id"] = str(result.inserted_id)
    return jsonify(categoria), 201

# 🔹 GET: obtener una categoría por ID (público)
@categorias_bp.route("/<string:id>", methods=["GET"])
def get_one(id):
    col = db["categorias"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    item = col.find_one({"_id": ObjectId(id)})
    if not item:
        return jsonify({"error": "No encontrado"}), 404
    item["_id"] = str(item["_id"])
    return jsonify(item), 200

# 🔹 PUT: actualizar una categoría (admin)
@categorias_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["categorias"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    data = request.json

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    return jsonify(updated), 200

# 🔹 DELETE: eliminar una categoría (admin)
@categorias_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["categorias"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify({"message": "Categoría eliminada correctamente"}), 200