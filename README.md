# Venelux Corporativo

Desarrollo del sitio web corporativo para Venelux bajo el patrón MVC, enfocado en alto rendimiento, seguridad y diseño usando el sistema de diseño generado por IA y ajustado.

## Requisitos de Instalación (Entorno XAMPP)

1. Clonar o ubicar esta carpeta en el directorio raíz de su servidor, ej. `C:\xampp\htdocs\Venelux`.
2. Asegurar que el entorno soporta PHP 8.4+ y PDO Extension habilitado.
3. Importar la Base de Datos: Abra PhpMyAdmin y en el tab de sentencias `SQL` o mediante importación de archivos, ejecute el contenido de **`database.sql`**. Esto creará la base de datos `venelux_db` y la tabla `form_contact`.
4. El servidor deberá interpretar correctamente el `RewriteEngine` del `.htaccess`.
5. Si experimenta problemas de enrutamiento al estar en diferentes subcarpetas de xampp, edite el archivo `app/core/Router.php`, variable `$basePath = '/Venelux/';` con la carpeta pertinente.
6. El proyecto incluye validación severa de seguridad con prepared statements (`Database.php`), `htmlspecialchars()`, `filter_var()` y encabezados XSS.

## Pruebas funcionales

- Abra `http://localhost/Venelux/` para ver la página dinámica usando los diseños provistos.
- Diríjase a la sección Contacto y use el formulario. El correo simulado se dispararía, pero está garantizado el guardado en MySQL.
- Diríjase a `http://localhost/Venelux/admin` para visualizar desde el panel de back-office los mensajes atrapados por la base de datos de forma segura.
