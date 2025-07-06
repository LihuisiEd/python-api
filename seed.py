from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["react-pf"]

# Limpiar todas las colecciones
db.clientes.delete_many({})
db.usuarios.delete_many({})
db.administradores.delete_many({})
db.categorias.delete_many({})
db.productos.delete_many({})
db.pedidos.delete_many({})
db.detalle_pedidos.delete_many({})

# Insertar cliente
cliente_id = db.clientes.insert_one({
    "nombres": "Juan",
    "apellidos": "Pérez",
    "correo": "juan@correo.com",
    "telefono": "123456789",
    "direccion": "Av. Los Álamos 123",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

# Insertar usuarios
admin_id = db.usuarios.insert_one({
    "nombre_usuario": "admin",
    "email": "admin@correo.com",
    "password": generate_password_hash("admin123"),
    "rol": "admin",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

cliente_user_id = db.usuarios.insert_one({
    "nombre_usuario": "cliente",
    "email": "cliente@correo.com",
    "password": generate_password_hash("cliente123"),
    "rol": "cliente",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

# Insertar en colección de administradores (aprovechando el user_id)
db.administradores.insert_one({
    "user_id": admin_id,
    "nombres": "Admin",
    "apellidos": "Principal",
    "cargo": "Gerente General",
    "telefono": "987654321"
})

# Categoría
categoria_id = db.categorias.insert_one({
    "nombre": "Snacks Veganos",
    "descripcion": "Deliciosos snacks sin productos de origen animal",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

# Productos
producto1_id = db.productos.insert_one({
    "nombre": "Chips de Kale",
    "descripcion": "Crujientes chips verdes",
    "stock": 100,
    "precio": 10.50,
    "categoria_id": categoria_id,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

producto2_id = db.productos.insert_one({
    "nombre": "Barra de Proteína Vegana",
    "descripcion": "Sabor cacao y almendras",
    "stock": 50,
    "precio": 7.90,
    "categoria_id": categoria_id,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

# Pedido y detalles
pedido_id = db.pedidos.insert_one({
    "cliente_id": cliente_id,
    "fecha": datetime.now(),
    "estado": "pendiente",
    "total": 18.40,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}).inserted_id

db.detalle_pedidos.insert_many([
    {
        "pedido_id": pedido_id,
        "producto_id": producto1_id,
        "cantidad": 1,
        "precio_unitario": 10.50,
        "subtotal": 10.50
    },
    {
        "pedido_id": pedido_id,
        "producto_id": producto2_id,
        "cantidad": 1,
        "precio_unitario": 7.90,
        "subtotal": 7.90
    }
])

print("Datos de prueba insertados correctamente.")
