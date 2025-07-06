from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from pymongo import MongoClient
from extensions import init_db 

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

# CORS
CORS(app, origins=Config.CORS_ORIGINS.split(","))

# JWT
jwt = JWTManager(app)

# MongoDB
client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# Blueprints
from routes.clientes import clientes_bp
from routes.usuarios import usuarios_bp
from routes.administradores import admin_bp
from routes.pedidos import pedidos_bp
from routes.categorias import categorias_bp
from routes.productos import productos_bp
from routes.detalle_pedidos import detalle_pedidos_bp
from routes.auth import auth_bp

# Registrar blueprints
app.register_blueprint(clientes_bp, url_prefix="/api/clientes")
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(admin_bp, url_prefix="/api/administradores")
app.register_blueprint(productos_bp, url_prefix="/api/productos")
app.register_blueprint(pedidos_bp, url_prefix="/api/pedidos")
app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
app.register_blueprint(detalle_pedidos_bp, url_prefix="/api/detalle-pedidos")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# Solo si ejecutas directamente (no en producción)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
