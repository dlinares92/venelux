from app import create_app, db
import sys

app = create_app()

with app.app_context():
    try:
        print("Iniciando creación de tablas en la base de datos...")
        db.create_all()
        print("¡Tablas creadas con éxito!")
    except Exception as e:
        print(f"Error al conectar con la base de datos o crear las tablas: {e}", file=sys.stderr)
        print("Por favor, asegúrate de que MySQL/MariaDB esté corriendo (XAMPP) en el puerto 3307 y que la base de datos 'venelux_db' exista.", file=sys.stderr)
        sys.exit(1)
