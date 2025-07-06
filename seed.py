from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
from faker import Faker

# Configuración inicial
fake = Faker('es_ES')
client = MongoClient("mongodb://localhost:27017/")
db = client["react-pf"]

# Limpiar colecciones
collections = [
    "clientes", "usuarios", "administradores", 
    "categorias", "productos", "pedidos", "detalle_pedidos"
]

for collection in collections:
    db[collection].delete_many({})

# --- 1. Usuarios y Administradores ---
admin_user = {
    "nombre_usuario": "admin_veggie",
    "email": "admin@veggiedelivery.com",
    "password": generate_password_hash("SuperAdmin123!"),
    "rol": "admin",
    "activo": True,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}
admin_id = db.usuarios.insert_one(admin_user).inserted_id

db.administradores.insert_one({
    "user_id": admin_id,
    "nombres": "Ana",
    "apellidos": "Vegana",
    "cargo": "Gerente General",
    "telefono": fake.phone_number(),
    "fecha_contratacion": datetime.now() - timedelta(days=365)
})

# --- 2. Clientes ---
clientes = []
for i in range(1, 6):
    cliente_user = {
        "nombre_usuario": f"cliente_{i}",
        "email": f"cliente{i}@mail.com",
        "password": generate_password_hash(f"Cliente{i}!"),
        "rol": "cliente",
        "activo": True,
        "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
        "updated_at": datetime.now()
    }
    user_id = db.usuarios.insert_one(cliente_user).inserted_id
    
    cliente = {
        "user_id": user_id,
        "nombres": fake.first_name(),
        "apellidos": fake.last_name(),
        "correo": cliente_user["email"],
        "telefono": fake.phone_number(),
        "direccion": fake.address(),
        "puntos_fidelidad": random.randint(0, 500),
        "created_at": cliente_user["created_at"],
        "updated_at": datetime.now()
    }
    cliente_id = db.clientes.insert_one(cliente).inserted_id
    clientes.append(cliente_id)

# --- 3. Categorías ---
categorias = [
    {
        "nombre": "Snacks Veganos",
        "descripcion": "Deliciosos snacks saludables sin ingredientes animales",
        "imagen": "snacks.jpg",
        "destacado": True
    },
    {
        "nombre": "Proteínas Vegetales",
        "descripcion": "Alternativas ricas en proteína 100% vegetal",
        "imagen": "proteinas.jpg",
        "destacado": True
    },
    {
        "nombre": "Lácteos Veganos",
        "descripcion": "Leches, quesos y yogures de origen vegetal",
        "imagen": "lacteos.jpg",
        "destacado": False
    },
    {
        "nombre": "Dulces Sin Culpa",
        "descripcion": "Postres y dulces sin azúcares refinados ni ingredientes animales",
        "imagen": "dulces.jpg",
        "destacado": True
    }
]
categorias_ids = [db.categorias.insert_one(cat).inserted_id for cat in categorias]

# --- 4. Productos ---
productos_data = [
    # Snacks Veganos
    {
        "nombre": "Chips de Kale Orgánico",
        "descripcion": "Chips crujientes de kale con sal marina",
        "precio": 12.90,
        "stock": 45,
        "categoria_id": categorias_ids[0],
        "marca": "VeggieCrunch",
        "valor_nutricional": {
            "calorias": 120,
            "proteinas": 3.5,
            "carbohidratos": 12,
            "grasas": 7
        },
        "ingredientes": ["kale", "aceite de oliva", "sal marina"],
        "etiquetas": ["orgánico", "sin gluten", "crudo"],
        "valoracion": 4.8,
        "imagenes": ["chips-kale-1.jpg", "chips-kale-2.jpg"],
        "destacado": True
    },
    {
        "nombre": "Mix de Frutos Secos",
        "descripcion": "Mezcla de almendras, nueces y anacardos tostados",
        "precio": 18.50,
        "stock": 32,
        "categoria_id": categorias_ids[0],
        "marca": "NaturaSnack",
        "valoracion": 4.6,
        "destacado": True
    },
    
    # Proteínas Vegetales
    {
        "nombre": "Hamburguesa de Lentejas",
        "descripcion": "Hamburguesa vegana alta en proteína",
        "precio": 9.90,
        "stock": 68,
        "categoria_id": categorias_ids[1],
        "marca": "GreenProtein",
        "valoracion": 4.5
    },
    {
        "nombre": "Tofu Ahumado",
        "descripcion": "Tofu orgánico con sabor ahumado",
        "precio": 7.50,
        "stock": 40,
        "categoria_id": categorias_ids[1],
        "marca": "SoyDelicious",
        "valoracion": 4.7,
        "destacado": True
    },
    
    # Lácteos Veganos
    {
        "nombre": "Queso Vegano de Anacardos",
        "descripcion": "Queso cremoso a base de anacardos",
        "precio": 14.90,
        "stock": 25,
        "categoria_id": categorias_ids[2],
        "marca": "NutCheese",
        "valoracion": 4.9,
        "destacado": True
    },
    
    # Dulces Sin Culpa
    {
        "nombre": "Brownie Sin Azúcar",
        "descripcion": "Brownie vegano endulzado con dátiles",
        "precio": 6.90,
        "stock": 50,
        "categoria_id": categorias_ids[3],
        "marca": "SweetVegan",
        "valoracion": 4.8
    }
]
productos_ids = [db.productos.insert_one(prod).inserted_id for prod in productos_data]

# --- 5. Pedidos y Detalles ---
estados_pedido = ["pendiente", "procesando", "enviado", "entregado", "cancelado"]
metodos_pago = ["tarjeta", "paypal", "transferencia"]

for i in range(1, 16):
    cliente_id = random.choice(clientes)
    fecha_pedido = datetime.now() - timedelta(days=random.randint(1, 60))
    estado = random.choices(
        estados_pedido,
        weights=[0.1, 0.2, 0.3, 0.35, 0.05],
        k=1
    )[0]
    
    # Crear pedido
    pedido = {
        "cliente_id": cliente_id,
        "fecha": fecha_pedido,
        "estado": estado,
        "metodo_pago": random.choice(metodos_pago),
        "direccion_entrega": fake.address(),
        "notas": fake.sentence() if random.random() > 0.7 else "",
        "created_at": fecha_pedido,
        "updated_at": fecha_pedido + timedelta(days=random.randint(1, 3)) if estado != "pendiente" else fecha_pedido
    }
    
    # Añadir detalles de entrega si ya fue enviado
    if estado in ["enviado", "entregado"]:
        pedido["fecha_envio"] = fecha_pedido + timedelta(days=1)
        pedido["seguimiento"] = f"VEG{random.randint(1000, 9999)}{random.choice('ABCDEFGH')}"
        
    if estado == "entregado":
        pedido["fecha_entrega"] = fecha_pedido + timedelta(days=random.randint(2, 5))
    
    # Insertar pedido
    pedido_id = db.pedidos.insert_one(pedido).inserted_id
    
    # Crear detalles del pedido
    num_productos = random.randint(1, 5)
    productos_pedido = random.sample(productos_ids, num_productos)
    detalles = []
    total_pedido = 0
    
    for prod_id in productos_pedido:
        producto = db.productos.find_one({"_id": prod_id})
        cantidad = random.randint(1, 3)
        subtotal = round(producto["precio"] * cantidad, 2)
        total_pedido += subtotal
        
        detalle = {
            "pedido_id": pedido_id,
            "producto_id": prod_id,
            "cantidad": cantidad,
            "precio_unitario": producto["precio"],
            "subtotal": subtotal,
            "comentario": fake.sentence() if random.random() > 0.8 else ""
        }
        detalles.append(detalle)
    
    # Insertar detalles y actualizar total del pedido
    db.detalle_pedidos.insert_many(detalles)
    db.pedidos.update_one(
        {"_id": pedido_id},
        {"$set": {"total": round(total_pedido, 2)}}
    )
    
    # Actualizar stock de productos
    for detalle in detalles:
        db.productos.update_one(
            {"_id": detalle["producto_id"]},
            {"$inc": {"stock": -detalle["cantidad"]}}
        )

# --- 6. Datos adicionales ---
# Cupones de descuento
db.cupones.insert_many([
    {
        "codigo": "BIENVENIDA10",
        "descuento": 10,
        "tipo": "porcentaje",
        "valido_desde": datetime.now() - timedelta(days=1),
        "valido_hasta": datetime.now() + timedelta(days=30),
        "usos_maximos": 100,
        "usos_actuales": 0,
        "activo": True
    },
    {
        "codigo": "VEGANLOVER",
        "descuento": 5,
        "tipo": "fijo",
        "valido_desde": datetime.now() - timedelta(days=10),
        "valido_hasta": datetime.now() + timedelta(days=15),
        "minimo_compra": 30,
        "activo": True
    }
])

# Reseñas de productos
for producto_id in productos_ids:
    for _ in range(random.randint(2, 8)):
        db.resenas.insert_one({
            "producto_id": producto_id,
            "cliente_id": random.choice(clientes),
            "valoracion": random.randint(3, 5),
            "comentario": fake.paragraph(),
            "fecha": datetime.now() - timedelta(days=random.randint(1, 90))
        })

print("¡Seed completado exitosamente!")
print(f"- {len(clientes)} clientes creados")
print(f"- {len(categorias_ids)} categorías creadas")
print(f"- {len(productos_ids)} productos creados")
print(f"- 15 pedidos de ejemplo generados")