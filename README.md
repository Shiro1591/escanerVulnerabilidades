# Escáner de Vulnerabilidades Web

Este proyecto es una aplicación de escritorio desarrollada en Python que permite analizar páginas web para detectar posibles vulnerabilidades básicas. Está pensado como proyecto de fin de ciclo y combina técnicas de escaneo de cabeceras HTTP, detección de formularios HTML y exportación de resultados.

## Funcionalidades principales

- **Escaneo de cabeceras HTTP**: detecta si faltan cabeceras de seguridad como `Content-Security-Policy` o `X-Frame-Options`.
- **Detección de formularios HTML**: identifica formularios y clasifica los campos potencialmente vulnerables (texto, email, password, etc.).
- **Escaneo completo**: ejecuta ambas funciones en conjunto (cabeceras + formularios).
- **Historial de escaneos**: muestra los resultados anteriores por URL.
- **Exportación**: permite guardar los resultados en formato JSON o CSV.
- **Interfaz gráfica**: construida con `ttkbootstrap` para un diseño limpio y moderno.

## Tecnologías utilizadas

- **Python 3**
- **Tkinter / ttkbootstrap** para la interfaz gráfica
- **SQLite** para la base de datos local
- **requests** y **BeautifulSoup** para el análisis web

## Estructura del proyecto
<pre>utils/
├── scanner.py         # Lógica de escaneo de cabeceras y formularios
├── db.py              # Acceso y gestión de la base de datos

db/
└── scanner.db         # Base de datos SQLite (se crea al ejecutar)

main_gui.py            # Interfaz gráfica principal
README.md              # Este archivo
requirements.txt       # Dependencias del proyecto</pre>
## Requisitos

Instala las dependencias necesarias con:

```bash
pip install -r requirements.txt

