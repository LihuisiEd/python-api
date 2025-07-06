from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required
from utils.auth import role_required

productos_bp = Blueprint("productos", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# Público: Listar productos
@productos_bp.route("/", methods=["GET"])
def get_all():
    col = db["productos"]
    productos = list(col.find())
    for p in productos:
        p["_id"] = str(p["_id"])
        p["categoria_id"] = str(p["categoria_id"])
    return jsonify(productos), 200

# Admin: Crear producto
@productos_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin")
def create():
    col = db["productos"]
    data = request.json
    required = ["nombre", "descripcion", "stock", "precio", "categoria_id"]
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if not is_valid_objectid(data["categoria_id"]):
        return jsonify({"error": "ID de categoría inválido"}), 400

    producto = {
        "nombre": data["nombre"],
        "descripcion": data["descripcion"],
        "stock": data["stock"],
        "precio": data["precio"],
        "categoria_id": ObjectId(data["categoria_id"])
    }
    result = col.insert_one(producto)
    producto["_id"] = str(result.inserted_id)
    producto["categoria_id"] = str(producto["categoria_id"])
    return jsonify(producto), 201

# Obtener por ID
@productos_bp.route("/<string:id>", methods=["GET"])
def get_one(id):
    col = db["productos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    item = col.find_one({"_id": ObjectId(id)})
    if not item:
        return jsonify({"error": "No encontrado"}), 404
    item["_id"] = str(item["_id"])
    item["categoria_id"] = str(item["categoria_id"])
    return jsonify(item), 200

# Actualizar producto
@productos_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["productos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    data = request.json
    if "categoria_id" in data and is_valid_objectid(data["categoria_id"]):
        data["categoria_id"] = ObjectId(data["categoria_id"])
    elif "categoria_id" in data:
        return jsonify({"error": "ID de categoría inválido"}), 400

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    updated["categoria_id"] = str(updated["categoria_id"])
    return jsonify(updated), 200

# Eliminar producto
@productos_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["productos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify({"message": "Producto eliminado correctamente"}), 200
