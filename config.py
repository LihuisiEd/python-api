import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "react-pf")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
