# Guarda esto en: streamcore/twitch_bot/twitch.py
import requests
import webbrowser
import http.server
import socketserver
import urllib.parse
import socket
import time
import threading
import json
import os

# --- Configuración ---
CLIENT_ID = "zvgk7f4guf7wg2qabfndt7i8xndklu"
CLIENT_SECRET = "nkai5gzmsiwf184cy7c234x0eufdtk" # Tu secret que sí funcionaba
REDIRECT_URI = "http://localhost:17563"
SCOPES = ["user:read:email", "chat:read", "chat:edit"]
AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TOKEN_FILE = "twitch_tokens.json" # Archivo para guardar la sesión
# --------------------

# --- 1. Servidor local para OAuth ---
class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    code = None
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            OAuthHandler.code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autenticacion completada. Puedes cerrar esta ventana.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Error: No se recibio el codigo OAuth.</h1>")

httpd_server = None # Para poder apagarlo
def wait_for_code():
    global httpd_server
    with socketserver.TCPServer(("localhost", 17563), OAuthHandler) as httpd:
        httpd_server = httpd
        print("⌛ (Twitch) Esperando respuesta de Twitch...")
        while OAuthHandler.code is None:
            httpd.handle_request()
        threading.Thread(target=httpd.shutdown).start() # Apaga el servidor
        return OAuthHandler.code

# --- 2. Lógica de Tokens (Pedir, Guardar, Cargar, Refrescar) ---
def open_oauth_browser():
    params = {"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "response_type": "code", "scope": " ".join(SCOPES)}
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("🌐 (Twitch) Abriendo navegador para autenticar...")
    webbrowser.open(url)

def get_access_token(code):
    data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code, "grant_type": "authorization_code", "redirect_uri": REDIRECT_URI}
    resp = requests.post(TOKEN_URL, data=data)
    resp.raise_for_status()
    return resp.json()

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=4)
    print(f"💾 (Twitch) Tokens guardados en '{TOKEN_FILE}'")

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def refresh_access_token(refresh_token):
    print("🔄 (Twitch) Refrescando token...")
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    resp = requests.post(TOKEN_URL, data=data)
    resp.raise_for_status()
    new_tokens = resp.json()
    if 'refresh_token' not in new_tokens:
        new_tokens['refresh_token'] = refresh_token
    return new_tokens

def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}", "Client-Id": CLIENT_ID}
    resp = requests.get("https://api.twitch.tv/helix/users", headers=headers)
    resp.raise_for_status()
    return resp.json()["data"][0]

# --- 3. Clase del Bot de Chat IRC ---
class TwitchChatBot:
    def __init__(self, username, token, channel):
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.username = username
        self.token = token
        self.channel = channel
        self.sock = socket.socket()
        self.running = True

    def connect(self):
        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS oauth:{self.token}\r\n".encode('utf-8'))
        self.sock.send(f"NICK {self.username}\r\n".encode('utf-8'))
        self.sock.send(f"JOIN #{self.channel}\r\n".encode('utf-8'))
        print(f"💬 (Twitch) Conectado al chat #{self.channel}")

    def send_message(self, message):
        self.sock.send(f"PRIVMSG #{self.channel} :{message}\r\n".encode('utf-8'))
        print(f"📤 (Twitch) Mensaje enviado: {message}")

    def listen_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data: break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    self.handle_line(line)
            except Exception as e:
                if self.running: print("⚠️ (Twitch) Error leyendo mensajes:", e)
                break
        print("🛑 (Twitch) Hilo de escucha detenido.")

    def handle_line(self, line):
        if line.startswith("PING"):
            self.sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
            return
        if "PRIVMSG" in line:
            parts = line.split("!", 1)
            username = parts[0][1:]
            message = line.split("PRIVMSG",1)[1].split(":",1)[1]
            print(f"(Twitch) {username}: {message}")
            if message.strip().lower() == "!ping":
                self.send_message(f"@{username} Pong!")

    def run(self):
        self.connect()
        self.send_message("✅ (Twitch) Bot listo y autenticado.")
        listener = threading.Thread(target=self.listen_messages, daemon=True)
        listener.start()
        
    def stop(self):
        self.running = False
        self.sock.close()
        print("🛑 (Twitch) Bot desconectado.")


# --- 4. Flujo Principal (Inicia todo) ---
if __name__ == "__main__":
    bot_instance = None
    try:
        tokens = load_tokens()
        access_token = None
        
        if tokens:
            print("✅ (Twitch) Tokens cargados desde archivo.")
            try:
                print("🕵️ (Twitch) Validando token...")
                access_token = tokens["access_token"]
                user = get_user_info(access_token)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    print("⚠️ (Twitch) Token expirado. Refrescando...")
                    try:
                        tokens = refresh_access_token(tokens["refresh_token"])
                        save_tokens(tokens)
                        access_token = tokens["access_token"]
                    except Exception as refresh_error:
                        print(f"❌ (Twitch) Error al refrescar: {refresh_error}")
                        tokens = None
                else: tokens = None
        
        if not tokens:
            print("🚀 (Twitch) Iniciando autenticación manual.")
            open_oauth_browser()
            code = wait_for_code()
            print(f"🔑 (Twitch) Código recibido: {code[:10]}...")
            tokens = get_access_token(code)
            save_tokens(tokens)
            access_token = tokens["access_token"]
            print("✅ (Twitch) Token nuevo guardado.")

        user = get_user_info(access_token)
        print(f"\n👤 (Twitch) Usuario autenticado: {user['display_name']} ({user['login']})")

        bot_instance = TwitchChatBot(username=user["login"], token=access_token, channel=user["login"])
        bot_instance.run()

        while True: time.sleep(1) # Mantiene el script vivo
            
    except KeyboardInterrupt:
        print("\n🛑 (Twitch) Cerrando bot...")
    finally:
        if bot_instance:
            bot_instance.stop()