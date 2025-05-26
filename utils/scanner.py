# Importaciones
import requests, sqlite3
from urllib.parse import urljoin
from bs4 import BeautifulSoup  
from utils.db import guardar_formulario, obtener_cabeceras_seguridad, guardar_ataque_detectado, obtener_errores_sql


# Método que escanea la URL y devuelve las cabeceras ausentes y presentes
def escanear_cabeceras(url):
    try:
        respuesta = requests.get(url, timeout=5)
        cabeceras = respuesta.headers
        ausentes = []

        cabeceras_referencia = obtener_cabeceras_seguridad()

        for cabecera in cabeceras_referencia:
            if cabecera not in cabeceras:
                ausentes.append(cabecera)

        return {
            "URL": url,
            "Código de Estado": respuesta.status_code,
            "Cabeceras Presentes": [c for c in cabeceras_referencia if c in cabeceras],
            "Cabeceras Ausentes": ausentes,
            
        }

    except requests.RequestException as e:
        return {
            "URL": url,
            "Error": str(e)
        }
     
# Método que escanea la URL y devuelve los formularios encontrados
def escanear_formularios(url):
    try:
        respuesta = requests.get(url, timeout=5)
        soup = BeautifulSoup(respuesta.text, "lxml")
        formularios = soup.find_all("form")

        if not formularios:

            # En caso de no encontrar formularios, se guarda un registro en la base de datos de todas formas
            guardar_formulario(
                url=url,
                metodo="N/A",
                accion="Ningún formulario encontrado",
                campo_nombre="-",
                campo_tipo="-",
                potencial=False
            )
            print("No se encontraron formularios en la página.")
            return

        print(f"Se encontraron {len(formularios)} formulario(s) en {url}:\n")

        for i, formulario in enumerate(formularios, start=1):
            metodo = formulario.get("method", "GET").upper()
            accion_cruda = formulario.get("action", "")
            accion = urljoin(url, accion_cruda)

            print(f"Formulario {i}:")
            print(f"Método: {metodo}")
            print(f"Acción: {accion}")

            inputs = formulario.find_all(["input", "textarea"])

                    
            for input_tag in inputs:
                tipo = input_tag.get("type", "text")
                nombre = input_tag.get("name", "")
                potencial = tipo in ["text", "search", "email", "password"]

                print(f"Campo: {nombre} (tipo: {tipo}) {'Potencialmente vulnerable' if potencial else ''}")

                guardar_formulario(
                    url=url,
                    metodo=metodo,
                    accion=accion,
                    campo_nombre=nombre,
                    campo_tipo=tipo,
                    potencial=potencial
                )

            print("-" * 40)

    except requests.RequestException as e:
        print(f"Error al acceder a la URL: {e}")

# Método que simula ataques usando los payloads sobre una URL concreta
def simular_ataques(url, tipo="Ambos"):
    conexion = sqlite3.connect("db/scanner.db")
    cursor = conexion.cursor()

    print(f"\n[Simulación de ataques en {url}]\n")

    # Recupera formularios potencialmente vulnerables
    cursor.execute("""
        SELECT metodo, accion, campo_nombre, campo_tipo
        FROM formularios_detectados
        WHERE url = ? AND potencialmente_vulnerable = 1
    """, (url,))
    formularios = cursor.fetchall()

    if not formularios:
        print("No hay formularios vulnerables registrados para esta URL.")
        conexion.close()
        return

    # Carga los payloads
    if tipo == "Ambos":
        cursor.execute("SELECT tipo, cadena FROM payloads")
    else:
        cursor.execute("SELECT tipo, cadena FROM payloads WHERE tipo = ?", (tipo,))
    payloads = cursor.fetchall()

    for metodo, accion, campo_nombre, campo_tipo in formularios:
        if not campo_nombre:
            continue  

    errores_sql = obtener_errores_sql()  

    for tipo, cadena in payloads:
        datos = {campo_nombre: cadena}
        url_destino = urljoin(url, accion)

        try:
            if metodo.upper() == "POST":
                respuesta = requests.post(url_destino, data=datos, timeout=5)
            else:
                respuesta = requests.get(url_destino, params=datos, timeout=5)

            contenido = respuesta.text.lower()
            vulnerabilidad = False

            if cadena.lower() in contenido:
                vulnerabilidad = True
                print("—" * 50)
                print(f"[!] POSIBLE VULNERABILIDAD DETECTADA ({tipo})")
                print(f"- Campo afectado: {campo_nombre}")
                print(f"- Payload usado: {cadena}")
                print(f"- Método: {metodo}")
                print(f"- Acción: {accion}\n")


            for error in errores_sql:
                if error in contenido:
                    vulnerabilidad = True
                    print(f"[!] ERROR SQL detectado en respuesta -> posible SQLi")
                    print(f"- Error detectado: {error}\n")


            evidencias = []
            if cadena.lower() in contenido:
                evidencias.append("Reflejo en respuesta")
            for error in errores_sql:
                if error in contenido:
                    evidencias.append("Error SQL detectado")

            evidencia_final = ", ".join(evidencias) if evidencias else "Sin evidencia directa"


            if vulnerabilidad:
                guardar_ataque_detectado(url, metodo, accion, campo_nombre, tipo, cadena, evidencia_final)
                print()

        except Exception as e:
            print(f"[X] Error al enviar payload a {url_destino}: {e}")

    conexion.close()


    try:
        if url.startswith("https://"):
            dominio = url.replace("https://", "").split("/")[0]
            http_url = f"http://{dominio}"
        elif url.startswith("http://"):
            http_url = url
        else:
            http_url = f"http://{url}"

        respuesta = requests.get(http_url, allow_redirects=False, timeout=5)

        location = respuesta.headers.get("Location", "")
        if location.startswith("https://"):
            return True
        else:
            return False
    except:
        return None  