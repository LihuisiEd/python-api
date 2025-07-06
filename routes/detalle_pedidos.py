from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required
from utils.auth import role_required

detalle_pedidos_bp = Blueprint("detalle_pedidos", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todos los detalles de pedidos (solo admin)
@detalle_pedidos_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all():
    col = db["detalle_pedidos"]
    items = list(col.find())
    for item in items:
        item["_id"] = str(item["_id"])
        item["pedido_id"] = str(item["pedido_id"])
        item["producto_id"] = str(item["producto_id"])
    return jsonify(items), 200

# 🔹 POST: crear nuevo detalle de pedido (cliente o admin)
@detalle_pedidos_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["admin", "cliente"])
def create():
    col = db["detalle_pedidos"]
    data = request.json
    required_fields = ["pedido_id", "producto_id", "cantidad", "precio_unitario", "subtotal"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if not is_valid_objectid(data["pedido_id"]) or not is_valid_objectid(data["producto_id"]):
        return jsonify({"error": "ID inválido"}), 400

    detalle = {
        "pedido_id": ObjectId(data["pedido_id"]),
        "producto_id": ObjectId(data["producto_id"]),
        "cantidad": data["cantidad"],
        "precio_unitario": data["precio_unitario"],
        "subtotal": data["subtotal"]
    }

    result = col.insert_one(detalle)
    detalle["_id"] = str(result.inserted_id)
    detalle["pedido_id"] = str(detalle["pedido_id"])
    detalle["producto_id"] = str(detalle["producto_id"])
    return jsonify(detalle), 201

# 🔹 GET: obtener un detalle por ID (cliente o admin)
@detalle_pedidos_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "cliente"])
def get_one(id):
    col = db["detalle_pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    item = col.find_one({"_id": ObjectId(id)})
    if not item:
        return jsonify({"error": "No encontrado"}), 404

    item["_id"] = str(item["_id"])
    item["pedido_id"] = str(item["pedido_id"])
    item["producto_id"] = str(item["producto_id"])
    return jsonify(item), 200

# 🔹 PUT: actualizar un detalle (solo admin)
@detalle_pedidos_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["detalle_pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    data = request.json
    if "pedido_id" in data and not is_valid_objectid(data["pedido_id"]):
        return jsonify({"error": "pedido_id inválido"}), 400
    if "producto_id" in data and not is_valid_objectid(data["producto_id"]):
        return jsonify({"error": "producto_id inválido"}), 400

    if "pedido_id" in data:
        data["pedido_id"] = ObjectId(data["pedido_id"])
    if "producto_id" in data:
        data["producto_id"] = ObjectId(data["producto_id"])

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    updated["pedido_id"] = str(updated["pedido_id"])
    updated["producto_id"] = str(updated["producto_id"])
    return jsonify(updated), 200

# 🔹 DELETE: eliminar un detalle (solo admin)
@detalle_pedidos_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["detalle_pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    return jsonify({"message": "Detalle eliminado correctamente"}), 200
