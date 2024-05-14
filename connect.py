# Código para crear la base de datos y las colecciones en MongoDB
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError


def connect_mongo():
    try:
        client = MongoClient("mongodb://root:1234@mongo:27017/")
        db = client["web_scraping"]
        logging.info("Conectado exitosamente a MongoDB: %s", db)
        return db
    except (ConnectionFailure, ConfigurationError) as e:
        logging.error("Error al conectar a MongoDB: %s", e)
        return None
