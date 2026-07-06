from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# Inicializar SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Vincular base de datos
    db.init_app(app)
    
    # Importar y registrar rutas
    with app.app_context():
        from app import routes
        
    return app
