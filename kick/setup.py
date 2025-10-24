# Guarda esto como: setup.py
import asyncio
import requests
import json
import webbrowser
import http.server
import socketserver
import threading
import subprocess
import time
from urllib.parse import urlparse, parse_qs
from kickpython import KickAPI

# --- Configuración ---
CLIENT_ID = "01K87Q01Q42DFJSDY02MG5BV1A"
CLIENT_SECRET = "48ecb09d8cd81424c57ba87c16c8503fb1c6c4d5ae8478532a835621c5442bb7"
REDIRECT_URI = "http://localhost:17563"
PORT = 17563
SCOPES = ["user:read", "channel:read", "chat:write", "events:subscribe"]
CONFIG_FILE = "config.json"
DB_FILE = "kick_tokens.db"
# ---------------------

# Evento para notificar al hilo principal que el código fue recibido
code_received_event = threading.Event()
code_container = {} # Usamos un dict para pasar el código
httpd_server = None # Para poder apagar el servidor

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador del servidor HTTP para atrapar el código OAuth."""
    def do_GET(self):
        global httpd_server
        query_components = parse_qs(urlparse(self.path).query)
        
        if "code" in query_components:
            code_container['code'] = query_components["code"][0]
            
            # Enviar respuesta al navegador
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>¡Autorización exitosa!</h1>".encode("utf-8"))
            self.wfile.write("<p>Puedes cerrar esta ventana. El bot se está iniciando...</p>".encode("utf-8"))
            # Notificar al hilo principal
            code_received_event.set()
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Error: No se recibio codigo.</h1>")

        # Apagar el servidor
        if httpd_server:
            threading.Thread(target=httpd_server.shutdown).start()

def start_http_server():
    """Inicia el servidor HTTP en un hilo separado."""
    global httpd_server
    try:
        with socketserver.TCPServer(("", PORT), OAuthCallbackHandler) as httpd:
            httpd_server = httpd
            print(f"🖥️  (Setup) Servidor temporal iniciado en http://localhost:{PORT}")
            print("⏳ (Setup) Esperando autorización del usuario...")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ (Setup) Error del servidor HTTP: {e}")
    print("🛑 (Setup) Servidor temporal detenido.")

async def main_setup():
    """Flujo principal de instalación asíncrona."""
    
    # 1. Iniciar el servidor web en un hilo
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()

    # 2. Inicializar API y obtener URL
    api = KickAPI(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        db_path=DB_FILE
    )
    auth_data = api.get_auth_url(SCOPES)
    
    # 3. Abrir el navegador
    print(f"🌐 (Setup) Abriendo navegador para autorización...")
    webbrowser.open(auth_data["auth_url"])
    
    # 4. Esperar a que el servidor reciba el código
    # Ejecutamos 'code_received_event.wait()' en un hilo
    # para no bloquear el bucle de asyncio
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, code_received_event.wait)
    
    if 'code' not in code_container:
        print("❌ (Setup) No se pudo obtener el código. Abortando.")
        await api.close()
        return

    code = code_container['code']
    print("🔑 (Setup) ¡Código OAuth recibido!")

    try:
        # 5. Intercambiar código por token (kickpython lo guarda en .db)
        print("🔃 (Setup) Intercambiando código por token...")
        token_data = await api.exchange_code(code, auth_data["code_verifier"])
        access_token = token_data['access_token']
        print(f"✅ (Setup) ¡Token guardado exitosamente en '{DB_FILE}'!")
        
        # 6. Obtener ID del canal (como tu broadcasterid.py)
        print("🔎 (Setup) Buscando información de tu canal...")
        url = "https://api.kick.com/public/v1/users"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Usamos requests en un executor para no bloquear
        response = await loop.run_in_executor(None, lambda: requests.get(url, headers=headers))
        response.raise_for_status()
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            user = data["data"][0]
            broadcaster_id = user["user_id"]
            username = user["name"]
            print(f"✅ (Setup) Canal encontrado: {username} (ID: {broadcaster_id})")

            # 7. Guardar configuración
            config_data = {"CHANNEL_NAME": username, "BROADCASTER_ID": broadcaster_id}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            print(f"✅ (Setup) Configuración guardada en '{CONFIG_FILE}'")
            
            # 8. Lanzar el bot
            print("\n" + "="*50)
            print("🚀 (Setup) ¡Instalación completa! Iniciando el bot...")
            print("="*50 + "\n")
            
            # Le damos 2 segundos al navegador para que muestre el "éxito"
            time.sleep(2) 
            
            # Ejecuta listener.py en un nuevo proceso
            subprocess.Popen(['py', 'listener.py'])
            
        else:
            print("❌ (Setup) No se pudo obtener información del usuario.")

    except Exception as e:
        print(f"\n❌ (Setup) Error en la instalación: {e}")
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main_setup())