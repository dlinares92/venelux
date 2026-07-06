import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'venelux-secret-key-192837465')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    SEND_FILE_MAX_AGE_DEFAULT = 86400  # 1 day (in seconds) for static assets caching
    
    # SQLAlchemy (MySQL/MariaDB) settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@127.0.0.1:3307/venelux_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Metadatos de proyectos corporativos (Traducidos de PHP)
    PROJECTS_METADATA = {
        'AVANTI BY FRIGILUX': {
            'cliente': 'Grupo Avanti / Frigilux',
            'ubicacion': 'Las Mercedes, Caracas',
            'fecha': '2023 - 2024',
            'trabajos': 'Remodelación integral de interiores premium, sistemas de iluminación avanzada e infraestructura IT de alta disponibilidad.'
        },
        'COMPLEJO DEPORTIVO SUNSET': {
            'cliente': 'Sunset World Group',
            'ubicacion': 'Litoral Central, La Guaira',
            'fecha': '2024 - En ejecución',
            'trabajos': 'Construcción de áreas recreativas, piscinas olímpicas y reforzamiento estructural de gradas monumentales.'
        },
        'COMPLEJO VACACIONAL LOS CARACAS': {
            'cliente': 'Gobernación del Estado La Guaira',
            'ubicacion': 'Los Caracas, La Guaira',
            'fecha': '2023 - 2024',
            'trabajos': 'Rehabilitación de fachadas, modernización de cabañas y diseño de paisajismo para entorno costero.'
        },
        'GALPONES  FRIGILUX': {
            'cliente': 'Inversiones Frigilux',
            'ubicacion': 'Zona Industrial Carabobo',
            'fecha': '2022 - 2023',
            'trabajos': 'Montaje de estructuras metálicas de gran envergadura, pavimentación industrial y sistemas contra incendios.'
        },
        'PEQUIVEN': {
            'cliente': 'Petroquímica de Venezuela (PEQUIVEN)',
            'ubicacion': 'Complejo Ana María Campos / El Tablazo',
            'fecha': '2023 - En ejecución',
            'trabajos': 'Mantenimiento mayor de plantas, suministro de tuberías de alta presión y obras civiles de contención.'
        },
        'UNIDAD EDUCATIVA KAVAC': {
            'cliente': 'Fundación Educativa Kavac',
            'ubicacion': 'Valencia, Carabobo',
            'fecha': '2023 - 2024',
            'trabajos': 'Ampliación de módulos escolares, diseño de laboratorios científicos y adecuación de áreas deportivas multifuncionales.'
        },
        'UNIVERSIDAD CENTRAL DE VENEZUELA': {
            'cliente': 'Comisión Presidencial para la Recuperación de la UCV',
            'ubicacion': 'Ciudad Universitaria de Caracas',
            'fecha': '2022 - 2024',
            'trabajos': 'Restauración de patrimonio arquitectónico, impermeabilización de naves y modernización de auditorios históricos.'
        }
    }
