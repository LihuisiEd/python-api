from pymongo import MongoClient
from flask import current_app

db = None

def init_db(app):
    global db
    client = MongoClient(app.config["MONGO_URI"])
    db = client[app.config["DB_NAME"]]
