# Escáner de Vulnerabilidades Web

Este proyecto es una aplicación de escritorio desarrollada en Python que permite analizar páginas web para detectar posibles vulnerabilidades básicas. Está pensado como proyecto de fin de ciclo (DAM) y combina técnicas de escaneo de cabeceras HTTP, detección de formularios HTML y simulación de ataques reflejados.

## Funcionalidades principales

- **Escaneo de cabeceras HTTP**: detecta si faltan cabeceras de seguridad como `Content-Security-Policy` o `X-Frame-Options`.
- **Detección de formularios HTML**: identifica formularios y clasifica campos potencialmente vulnerables (como `text`, `email`, `password`, etc.).
- **Simulación de ataques**: permite lanzar payloads de tipo XSS y SQLi contra formularios detectados, identificando posibles vulnerabilidades por reflejo o errores SQL.
- **Registro de evidencia**: almacena si el payload fue reflejado o si se detectó un error SQL en la respuesta.
- **Historial de escaneos**: muestra los resultados anteriores por URL, incluyendo cabeceras, formularios y ataques detectados.
- **Exportación**: permite guardar los resultados en formato JSON o CSV (cabeceras, formularios y ataques).
- **Contador en la interfaz**: muestra cuántos ataques han sido detectados en total.
- **Interfaz gráfica**: construida con `ttkbootstrap`

## Tecnologías utilizadas

- **Python 3**
- **Tkinter + ttkbootstrap** (interfaz gráfica)
- **SQLite3** (base de datos local)
- **requests** y **BeautifulSoup** (análisis de páginas web)
- **json**, **csv**, **os**, **platform**, etc.

## Estructura del proyecto
```
utils/
├──── scanner.py # Lógica de escaneo de cabeceras y formularios
└──── db.py # Acceso y gestión de la base de datos
db/
└──── scanner.db # Base de datos SQLite (se crea al ejecutar)
main.py # Interfaz gráfica principal
README.md # Este archivo
```
## Requisitos

Instala las dependencias necesarias con:

```bash
pip install -r requirements.txt
```
Si no tienes "ttkbootstrap" instalalo con:
```
pip install ttkbootstrap
