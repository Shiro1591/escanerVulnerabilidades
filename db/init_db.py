# Importaciones 
import sqlite3
import os

# Método que inicializa la base de datos y crea las tablas necesarias
def init_db():

    # Verifica si la carpeta "db" existe, si no, la crea
    if not os.path.exists("db"):
        print("Creando Base de Datos...")
        os.makedirs("db")

    conn = sqlite3.connect("db/scanner.db")
    cursor = conn.cursor()

    # Ejecuta el script para crear las tablas
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS resultados_escaneos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            fecha_escaneo TEXT,
            nivel_riesgo TEXT,
            vulnerabilidades TEXT
        );

        CREATE TABLE IF NOT EXISTS payloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            cadena TEXT NOT NULL,
            descripcion TEXT
        );

        CREATE TABLE IF NOT EXISTS cabeceras_seguridad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cabecera TEXT NOT NULL,
            valor_recomendado TEXT,
            descripcion TEXT
        );
                         
        CREATE TABLE IF NOT EXISTS formularios_detectados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            metodo TEXT,
            accion TEXT,
            campo_nombre TEXT,
            campo_tipo TEXT,
            potencialmente_vulnerable INTEGER,
            id_resultado INTEGER,
            FOREIGN KEY (id_resultado) REFERENCES resultados_escaneos(id)
        );

        CREATE TABLE IF NOT EXISTS ataques_detectados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            metodo TEXT,
            accion TEXT,
            campo_nombre TEXT,
            tipo_payload TEXT,
            payload TEXT,
            evidencia TEXT,
            fecha TEXT,
            id_resultado INTEGER,
            id_payload INTEGER,
            FOREIGN KEY (id_resultado) REFERENCES resultados_escaneos(id),
            FOREIGN KEY (id_payload) REFERENCES payloads(id)
        );

                         
        CREATE TABLE IF NOT EXISTS errores_sql (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patron TEXT NOT NULL,
            descripcion TEXT
        );

    """)

     # Inserta las cabeceras de seguridad en la tabla cabeceras_seguridad, eb caso de que este vacía
    cursor.execute("SELECT COUNT(*) FROM cabeceras_seguridad")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO cabeceras_seguridad (nombre_cabecera, valor_recomendado, descripcion)
            VALUES (?, ?, ?)
        """, [
            ("X-Frame-Options", "DENY", "Evita que la página se cargue dentro de un iframe."),
            ("X-XSS-Protection", "1; mode=block", "Activa protección contra ataques XSS."),
            ("Strict-Transport-Security", "max-age=63072000; includeSubDomains", "Fuerza el uso de HTTPS."),
            ("Content-Security-Policy", "default-src 'self'", "Define políticas de carga de recursos."),
            ("Referrer-Policy", "no-referrer", "Controla la información enviada en el encabezado Referer.")
        ])

        # Inserta payloads comunes en la tabla de payloads, en caso de que este vacía
        cursor.execute("SELECT COUNT(*) FROM payloads")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
            "INSERT INTO payloads (tipo, cadena, descripcion) VALUES (?, ?, ?)",
            [
                # XSS
                ("XSS", "<script>alert(1)</script>", "Alerta básica de JavaScript"),
                ("XSS", "\"><svg/onload=alert(1)>", "XSS SVG con onload"),
                ("XSS", "<img src=x onerror=alert(1)>", "XSS por imagen maliciosa"),
                ("XSS", "<body onload=alert('XSS')>", "XSS usando body onload"),

                # SQLi
                ("SQLi", "' OR '1'='1", "Bypass autenticación básica"),
                ("SQLi", "' OR 1=1--", "Consulta booleana verdadera"),
                ("SQLi", "'; DROP TABLE users;--", "Intento de eliminación de tabla"),
                ("SQLi", "\" OR \"\" = \"", "Variación con comillas dobles")
            ]
        )
            
        # Inserta patrones de errores SQL en la tabla errores_sql, en caso de que este vacía
        cursor.execute("SELECT COUNT(*) FROM errores_sql")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO errores_sql (patron, descripcion)
                VALUES (?, ?)
            """, [
                ("you have an error in your sql syntax", "MySQL: error típico de sintaxis"),
                ("warning: mysql", "MySQL: advertencia general"),
                ("unclosed quotation mark", "SQL Server: comillas sin cerrar"),
                ("quoted string not properly terminated", "Oracle: string mal cerrado"),
                ("sql syntax error", "Genérico: error de sintaxis SQL"),
                ("ora-01756", "Oracle: string literal no cerrado"),
                ("mysql_fetch", "MySQL: error en fetch"),
                ("syntax error", "Genérico: error de sintaxis")
            ])



    # Hace commit para guardar los cambios y cierra la conexión
    conn.commit()
    conn.close()

    # Ejecuta la función que crea la BD solo si se esta ejecutando directamente
if __name__ == "__main__":
    init_db()
