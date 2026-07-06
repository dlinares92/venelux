import os
import shutil
import sys

# Add the python folder to sys.path so we can import the app modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def build_static():
    app = create_app()
    # Use Flask's built-in test client to render routes without running the server
    client = app.test_client()
    
    # Define the output directory (dist at the root of the project)
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dist'))
    print(f"--- Iniciando compilación estática en: {dist_dir} ---")
    
    # Clean up previous builds
    if os.path.exists(dist_dir):
        print("Eliminando carpeta 'dist' previa...")
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy static assets (CSS, JS, images, videos) to dist/static
    static_src = os.path.join(app.root_path, 'static')
    static_dst = os.path.join(dist_dir, 'static')
    if os.path.exists(static_src):
        print(f"Copiando archivos estáticos desde {static_src} -> {static_dst}...")
        shutil.copytree(static_src, static_dst)
        
        # Copy logo.png to favicon.ico in the dist root folder to prevent 404s
        logo_path = os.path.join(static_src, 'img', 'logo.png')
        favicon_path = os.path.join(dist_dir, 'favicon.ico')
        if os.path.exists(logo_path):
            print(f"Copiando favicon: {logo_path} -> {favicon_path}")
            shutil.copy(logo_path, favicon_path)
    else:
        print("ERROR: No se encontró la carpeta 'static' en la app Flask.", file=sys.stderr)
        return

    # Define routes to render and their corresponding static HTML file names
    pages = {
        '/': 'index.html',
        '/index': 'index.html',
        '/servicios': 'servicios.html',
        '/nosotros': 'nosotros.html',
        '/contacto': 'contacto.html'
    }
    
    # Render each page
    with app.app_context():
        for route, filename in pages.items():
            print(f"Renderizando ruta: {route} -> {filename}")
            response = client.get(route)
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # Make all asset paths relative for maximum portability
                html_content = html_content.replace('href="/static/', 'href="static/')
                html_content = html_content.replace('src="/static/', 'src="static/')
                html_content = html_content.replace('poster="/static/', 'poster="static/')
                html_content = html_content.replace('"/static/img/', '"static/img/')
                html_content = html_content.replace('`/static/img/', '`static/img/')
                
                # Convert routing paths to point to correct static files
                html_content = html_content.replace('href="/#', 'href="index.html#')
                html_content = html_content.replace('href="/index#', 'href="index.html#')
                html_content = html_content.replace('href="/nosotros"', 'href="nosotros.html"')
                html_content = html_content.replace('href="/servicios"', 'href="servicios.html"')
                html_content = html_content.replace('href="/contacto"', 'href="contacto.html"')
                html_content = html_content.replace('action="/contacto"', 'action="contacto.html"')
                
                # Also handle clean URL cases in footer/nav just in case
                html_content = html_content.replace('href="/index"', 'href="index.html"')
                
                # Write to the destination file
                dest_path = os.path.join(dist_dir, filename)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"  [OK] Escrito {filename}")
            else:
                print(f"ERROR: No se pudo renderizar la ruta {route}. Código de estado: {response.status_code}", file=sys.stderr)
                
    # Create a simple _redirects file for Cloudflare Pages to handle pretty URLs if needed
    # e.g., mapping /nosotros to /nosotros.html
    # Cloudflare Pages does this automatically, but having this file ensures correct routing.
    redirects_path = os.path.join(dist_dir, '_redirects')
    with open(redirects_path, 'w', encoding='utf-8') as f:
        f.write("/index.html /index 301\n")
        f.write("/servicios /servicios.html 200\n")
        f.write("/nosotros /nosotros.html 200\n")
        f.write("/contacto /contacto.html 200\n")
    print("  [OK] Creado archivo '_redirects' para Cloudflare Pages.")
                
    print("\n--- ¡Compilación estática completada con éxito! ---")
    print(f"Ubicación de la build lista para Cloudflare: {dist_dir}")
    print("Puedes subir esta carpeta 'dist' directamente a Cloudflare Pages.")

if __name__ == '__main__':
    build_static()
