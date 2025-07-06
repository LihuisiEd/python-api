from flask import Blueprint, request, jsonify
from bson import ObjectId, errors
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import role_required

clientes_bp = Blueprint("clientes", __name__)

def is_valid_objectid(id):
    try:
        ObjectId(id)
        return True
    except (errors.InvalidId, TypeError):
        return False

# 🔹 GET: listar todos los clientes (solo admin)
@clientes_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all():
    col = db["clientes"]
    clientes = list(col.find())
    for cliente in clientes:
        cliente["_id"] = str(cliente["_id"])
    return jsonify(clientes), 200

# 🔹 POST: registrar cliente (registro público)
@clientes_bp.route("/", methods=["POST"])
def create():
    col = db["clientes"]
    data = request.json
    required = ["nombres", "apellidos", "correo", "telefono", "direccion"]
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    result = col.insert_one(data)
    new_cliente = col.find_one({"_id": result.inserted_id})
    new_cliente["_id"] = str(new_cliente["_id"])
    return jsonify(new_cliente), 201

# 🔹 GET: obtener un cliente por ID (cliente o admin)
@clientes_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "cliente"])
def get_one(id):
    col = db["clientes"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    current_user_id = get_jwt_identity()
    if current_user_id != id and not request.jwt_role == "admin":
        return jsonify({"error": "No autorizado"}), 403

    cliente = col.find_one({"_id": ObjectId(id)})
    if not cliente:
        return jsonify({"error": "No encontrado"}), 404

    cliente["_id"] = str(cliente["_id"])
    return jsonify(cliente), 200

# 🔹 PUT: actualizar cliente (cliente o admin)
@clientes_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "cliente"])
def update(id):
    col = db["clientes"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    current_user_id = get_jwt_identity()
    if current_user_id != id and not request.jwt_role == "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.json
    result = col.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    updated = col.find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    return jsonify(updated), 200

# 🔹 DELETE: eliminar cliente (solo admin)
@clientes_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete(id):
    col = db["clientes"]
    if not is_valid_objectid(id):
        return jsonify({"error": "ID inválido"}), 400

    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "No encontrado"}), 404

    return jsonify({"message": "Cliente eliminado correctamente"}), 200
