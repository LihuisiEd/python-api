from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import role_required
from bson import ObjectId, errors
from extensions import db

pedidos_bp = Blueprint("pedidos", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todos los pedidos (solo admin)
@pedidos_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all():
    col = db["pedidos"]
    items = list(col.find())
    for item in items:
        item["_id"] = str(item["_id"])
        item["cliente_id"] = str(item["cliente_id"])
    return jsonify(items), 200

# 🔹 POST: crear un nuevo pedido (solo cliente)
@pedidos_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("cliente")
def create_pedido():
    col = db["pedidos"]
    data = request.json
    user_id = get_jwt_identity()

    if "total" not in data:
        return jsonify({"error": "Falta el campo 'total'"}), 400

    pedido = {
        "cliente_id": ObjectId(user_id),
        "fecha": data.get("fecha"),
        "estado": data.get("estado", "pendiente"),
        "total": data["total"]
    }

    result = col.insert_one(pedido)

    response = {
        "_id": str(result.inserted_id),
        "cliente_id": str(pedido["cliente_id"]),
        "fecha": pedido.get("fecha"),
        "estado": pedido["estado"],
        "total": pedido["total"]
    }

    return jsonify(response), 201

# 🔹 GET: obtener pedido por ID (cliente o admin)
@pedidos_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "cliente"])
def get_one(id):
    col = db["pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    pedido = col.find_one({"_id": ObjectId(id)})
    if not pedido:
        return jsonify({"error": "No encontrado"}), 404

    current_user = get_jwt_identity()
    if str(pedido["cliente_id"]) != current_user and not role_required("admin")(lambda: True)():
        return jsonify({"error": "No autorizado"}), 403

    pedido["_id"] = str(pedido["_id"])
    pedido["cliente_id"] = str(pedido["cliente_id"])
    return jsonify(pedido), 200

# 🔹 PUT: actualizar pedido (solo admin)
@pedidos_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update(id):
    col = db["pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    data = request.json
    if "cliente_id" in data and not is_valid_objectid(data["cliente_id"]):
        return jsonify({"error": "cliente_id inválido"}), 400

    if "cliente_id" in data:
        data["cliente_id"] = ObjectId(data["cliente_id"])

    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    updated["cliente_id"] = str(updated["cliente_id"])
    return jsonify(updated), 200

# 🔹 DELETE: eliminar pedido (solo admin)
@pedidos_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["pedidos"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    return jsonify({"message": "Pedido eliminado correctamente"}), 200

# 🔹 GET: obtener pedido con detalle del cliente (solo admin)
@pedidos_bp.route("/detalle/<string:id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_pedido_con_cliente(id):
    col = db["pedidos"]
    clientes_col = db["clientes"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    pedido = col.find_one({"_id": ObjectId(id)})
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    cliente = clientes_col.find_one({"_id": pedido["cliente_id"]})
    if cliente:
        cliente["_id"] = str(cliente["_id"])
        pedido["cliente"] = cliente

    pedido["_id"] = str(pedido["_id"])
    pedido["cliente_id"] = str(pedido["cliente_id"])
    return jsonify(pedido), 200

# 🔹 GET: listar pedidos de un cliente (cliente o admin)
@pedidos_bp.route("/cliente/<string:cliente_id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "cliente"])
def listar_pedidos_cliente(cliente_id):
    col = db["pedidos"]
    if not is_valid_objectid(cliente_id):
        return jsonify({"error": "ID inválido"}), 400

    current_user = get_jwt_identity()

    if current_user != cliente_id and not role_required("admin")(lambda: True)():
        return jsonify({"error": "No autorizado"}), 403

    pedidos = list(col.find({"cliente_id": ObjectId(cliente_id)}))
    for p in pedidos:
        p["_id"] = str(p["_id"])
        p["cliente_id"] = str(p["cliente_id"])
    return jsonify(pedidos), 200
