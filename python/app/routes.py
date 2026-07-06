import os
import re
import time
from functools import wraps
from flask import current_app as app, render_template, request, redirect, url_for, send_from_directory, make_response
import bleach
from app import db
from app.models import ContactMessage
from flask_mail import Message, Mail

mail = Mail(app)

# --- Server-Side HTML Page Cache (in-memory) ---
class SimpleMemoryCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        if key in self.store:
            data, expiry = self.store[key]
            if time.time() < expiry:
                return data
            else:
                del self.store[key]
        return None

    def set(self, key, value, timeout):
        self.store[key] = (value, time.time() + timeout)

    def clear(self):
        self.store.clear()

page_cache = SimpleMemoryCache()

def cache_page(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # Key based on full URL path & query parameters
            cache_key = request.full_path
            cached_val = page_cache.get(cache_key)
            if cached_val is not None:
                resp = make_response(cached_val['data'])
                resp.status_code = cached_val['status_code']
                resp.headers.update(cached_val['headers'])
                resp.headers['X-Cache-Status'] = 'HIT'
                return resp
            
            resp = make_response(f(*args, **kwargs))
            if resp.status_code == 200:
                cached_data = {
                    'data': resp.get_data(),
                    'status_code': resp.status_code,
                    'headers': dict(resp.headers)
                }
                page_cache.set(cache_key, cached_data, timeout)
            resp.headers['X-Cache-Status'] = 'MISS'
            return resp
        return decorated_function
    return decorator


# --- Project list cache (avoid re-scanning disk on every request) ---
_projects_cache = None
_projects_cache_time = 0
_CACHE_TTL = 300  # seconds (5 minutes)

# Helper function to find and list all project folders and files
def get_projects():
    global _projects_cache, _projects_cache_time
    now = time.time()
    if _projects_cache is not None and (now - _projects_cache_time) < _CACHE_TTL:
        return _projects_cache

    possible_paths = [
        os.path.join(app.root_path, 'static', 'img', 'PROYECTOS VENELUX'),
        os.path.abspath(os.path.join(app.root_path, '..', '..', 'public', 'img', 'PROYECTOS VENELUX')),
        os.path.abspath(os.path.join(app.root_path, '..', '..', 'public', 'img', 'PROYECTOS%20VENELUX')),
    ]
    
    base_path = None
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            base_path = path
            break
            
    projects = []
    if not base_path:
        _projects_cache = projects
        _projects_cache_time = now
        return projects

    try:
        folders = sorted(os.listdir(base_path))
    except Exception:
        return projects

    for folder_name in folders:
        dir_path = os.path.join(base_path, folder_name)
        if os.path.isdir(dir_path):
            project_files = []
            try:
                files = os.listdir(dir_path)
            except Exception:
                continue
                
            for file in files:
                ext = file.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'mp4']:
                    project_files.append(file)
            
            def sort_key(filename):
                is_mp4 = filename.lower().endswith('.mp4')
                return (is_mp4, filename.lower())
                
            project_files.sort(key=sort_key)
            
            meta = app.config['PROJECTS_METADATA'].get(folder_name, {
                'cliente': 'Por definir',
                'ubicacion': 'Por definir',
                'fecha': 'Pendiente',
                'trabajos': 'Reseña en preparación.'
            })
            
            projects.append({
                'folder': folder_name,
                'meta': meta,
                'files': project_files
            })

    _projects_cache = projects
    _projects_cache_time = now
    return projects


def _cached_response(resp, max_age=86400):
    """Add browser cache headers to a response (default 24h for images)."""
    resp.headers['Cache-Control'] = f'public, max-age={max_age}, stale-while-revalidate=3600'
    resp.headers['Vary'] = 'Accept-Encoding'
    return resp

# Asset loaders for retro-compatibility with PHP URL paths
@app.route('/Venelux/public/img/PROYECTOS%20VENELUX/<path:filename>')
@app.route('/Venelux/public/img/PROYECTOS VENELUX/<path:filename>')
@app.route('/static/img/PROYECTOS VENELUX/<path:filename>')
def serve_project_media(filename):
    static_media_path = os.path.join(app.root_path, 'static', 'img', 'PROYECTOS VENELUX')
    if os.path.exists(os.path.join(static_media_path, filename)):
        return _cached_response(make_response(send_from_directory(static_media_path, filename)))
        
    php_media_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'public', 'img', 'PROYECTOS VENELUX'))
    if os.path.exists(os.path.join(php_media_path, filename)):
        return _cached_response(make_response(send_from_directory(php_media_path, filename)))
        
    return "File not found", 404

@app.route('/Venelux/img/<path:filename>')
@app.route('/Venelux/public/img/<path:filename>')
def serve_generic_img(filename):
    static_img_path = os.path.join(app.root_path, 'static', 'img')
    if os.path.exists(os.path.join(static_img_path, filename)):
        return _cached_response(make_response(send_from_directory(static_img_path, filename)))
        
    php_img_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'public', 'img'))
    if os.path.exists(os.path.join(php_img_path, filename)):
        return _cached_response(make_response(send_from_directory(php_img_path, filename)))
        
    return "File not found", 404

@app.route('/Venelux/public/js/<path:filename>')
def serve_js(filename):
    static_js_path = os.path.join(app.root_path, 'static', 'js')
    if os.path.exists(os.path.join(static_js_path, filename)):
        return _cached_response(make_response(send_from_directory(static_js_path, filename)))
        
    php_js_path = os.path.abspath(os.path.join(app.root_path, '..', '..', 'public', 'js'))
    if os.path.exists(os.path.join(php_js_path, filename)):
        return _cached_response(make_response(send_from_directory(php_js_path, filename)))
        
    return "File not found", 404


# --- APPLICATION ROUTES ---

@app.route('/')
@app.route('/index')
@cache_page(300)
def index():
    projects = get_projects()
    return render_template('home.html', title='Inicio | Venelux Construcciones', projects=projects)

@app.route('/servicios')
@cache_page(300)
def services():
    services_list = [
        {
            'title': 'Remodelación de Interiores',
            'description': 'Renovamos espacios combinando estética moderna y una funcionalidad óptima, usando materiales premium.'
        },
        {
            'title': 'Infraestructura IT',
            'description': 'Diseñamos y construimos redes estructuradas, cuartos de servidores (data centers) y sistemas eléctricos.'
        },
        {
            'title': 'Especialistas en Construcción de Galpones',
            'description': 'Construimos galpones industriales llave en mano, desde las zapatas hasta las vigas de acero y revestimientos.'
        },
        {
            'title': 'Maquinarias de Construcción',
            'description': 'Alquiler y servicio de maquinaria pesada: retroexcavadoras, grúas y tractores del más alto rendimiento.'
        },
        {
            'title': 'Construcción General',
            'description': 'Proyectos residenciales y corporativos, desde los cimientos hasta los toques finales.'
        }
    ]
    return render_template('services.html', title='Nuestros Servicios | Venelux', services=services_list)

@app.route('/nosotros')
@cache_page(300)
def about():
    return render_template('about.html', title='Nosotros | Venelux Construcciones')

@app.route('/contacto', methods=['GET', 'POST'])
@cache_page(300)
def contact():
    if request.method == 'POST':
        # XSS protection and validation
        name = bleach.clean(request.form.get('name', '').strip())
        email = bleach.clean(request.form.get('email', '').strip())
        message = bleach.clean(request.form.get('message', '').strip())
        
        # Validations
        if not name or not email or not message:
            return render_template('contact.html', title='Contacto | Venelux', error='Todos los campos son requeridos.')
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return render_template('contact.html', title='Contacto | Venelux', error='Correo electrónico no válido.')
            
        try:
            # Save message to DB
            msg_obj = ContactMessage(name=name, email=email, message=message)
            db.session.add(msg_obj)
            db.session.commit()
            
            # Send Notification Email (safe execution with try-catch)
            try:
                msg = Message(
                    subject='Nuevo Mensaje de Contacto - Sitio Web',
                    sender=(name, email),
                    recipients=['admin@venelux.com'],
                    body=f"Nombre: {name}\nCorreo: {email}\n\nMensaje:\n{message}\n"
                )
                mail.send(msg)
            except Exception:
                # Silence email failure if local SMTP is not configured (like PHP's @mail)
                pass
                
            return render_template('contact.html', title='Contacto | Venelux', success='Gracias por escribirnos. Nos pondremos en contacto pronto.')
            
        except Exception as e:
            db.session.rollback()
            return render_template('contact.html', title='Contacto | Venelux', error=f'Ocurrió un error guardando el mensaje: {str(e)}')
            
    return render_template('contact.html', title='Contacto | Venelux')

@app.route('/admin')
def admin():
    try:
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        error = None
    except Exception as e:
        messages = []
        error = f"No se pueden cargar los mensajes: La Base de Datos no ha sido configurada o inicializada ('venelux_db'). Error: {str(e)}"
        
    return render_template('admin.html', title='Panel de Administración | Venelux', messages=messages, error=error)
