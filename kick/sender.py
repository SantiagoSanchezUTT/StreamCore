# Guarda esto como: sender.py
import json
import requests
import sys
import sqlite3

# --- CAMBIO: Eliminamos el bloque 'sys.stdout.reconfigure' ---
# Ya no es necesario, el listener se encargará

CONFIG_FILE = "config.json"
DB_FILE = "kick_tokens.db"

# 1. Función para leer el token MÁS RECIENTE de la DB
def get_latest_token():
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT access_token FROM tokens ORDER BY expires_at DESC LIMIT 1")
        result = cur.fetchone()
        con.close()
        return result[0] if result else None
    except Exception as e:
        print(f"(Sender) Error al leer DB: {e}")
        return None

# 2. Función para leer el ID del config
def get_broadcaster_id():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('BROADCASTER_ID')
    except Exception as e:
        print(f"(Sender) Error al leer config: {e}")
        return None

# 3. Obtener el mensaje del argumento
if len(sys.argv) < 2:
    print("(Sender) Error: No se proporcionó ningún mensaje.")
    sys.exit(1)
MENSAJE = sys.argv[1]

# 4. Configuración dinámica
ACCESS_TOKEN = get_latest_token()
BROADCASTER_ID = get_broadcaster_id()

if not ACCESS_TOKEN or not BROADCASTER_ID:
    print("(Sender) Error: Falta Token o ID.")
    print("Asegúrate de haber ejecutado 'setup.py' primero.")
    sys.exit(1)

# 5. Preparar request (Tu lógica V1 que funciona)
url = "https://api.kick.com/public/v1/chat"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
payload = {"broadcaster_user_id": BROADCASTER_ID, "content": MENSAJE, "type": "user"}

# 6. Enviar mensaje
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"(Sender) Mensaje '{MENSAJE}' enviado.")
    else:
        print(f"(Sender) Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"(Sender) Excepción: {e}")