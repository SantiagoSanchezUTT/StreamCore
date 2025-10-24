# Guarda esto como: listener.py
import asyncio
import asyncio.subprocess
import json
from kickpython import KickAPI

# --- Configuración ---
CONFIG_FILE = "config.json"
SCRIPT_ENVIADOR = "sender.py"
# ---------------------

# 1. Leer configuración
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    CHANNEL_NAME = config['CHANNEL_NAME']
except FileNotFoundError:
    print(f"❌ (Listener) Error: No se encuentra '{CONFIG_FILE}'.")
    print("(Listener) Ejecuta 'setup.py' primero.")
    exit()
except KeyError:
    print(f"❌ (Listener) Error: '{CONFIG_FILE}' está corrupto.")
    exit()

# 2. Inicializa la API
api = KickAPI(
    db_path="kick_tokens.db" 
)

# 3. Función para llamar al script que envía mensajes
async def ejecutar_envio(mensaje: str):
    print(f"➡️  (Listener) Disparando 'sender.py' con el mensaje: '{mensaje}'")
    try:
        # --- CAMBIO 1: Quitamos el 'encoding="utf-8"' ---
        proc = await asyncio.create_subprocess_exec(
            'py', SCRIPT_ENVIADOR, mensaje,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            # --- CAMBIO 2: Añadimos errors='replace' ---
            # Si no puede leer un acento, pondrá '?' en lugar de crashear
            print(f"✅  (Listener) 'sender.py' terminó: {stdout.decode(errors='replace').strip()}")
        else:
            # --- CAMBIO 3: Añadimos errors='replace' ---
            print(f"❌  (Listener) 'sender.py' falló: {stderr.decode(errors='replace').strip()}")
            
    except Exception as e:
        print(f"❌  (Listener) Error al llamar subproceso: {e}")

# 4. Controlador de mensajes
async def mi_controlador_de_mensajes(message: dict):
    content = message.get('content', '')
    sender = message.get('sender_username', 'Desconocido')
    print(f"💬  {sender}: {content}")
    
    if content.strip().lower() == "!ping":
        await ejecutar_envio("¡pong!")
    elif content.strip().lower() == "!hola":
        await ejecutar_envio(f"¡Hola {sender}! 👋")
    elif content.strip().lower() == "!redes":
        await ejecutar_envio("¡Sígueme en mis redes! www.ejemplo.com")

# 5. Función principal
async def main():
    try:
        api.add_message_handler(mi_controlador_de_mensajes)
        print("🎧 (Listener) Controlador de mensajes registrado.")

        print(f"🔌 (Listener) Conectando al chatroom de {CHANNEL_NAME}...")
        await api.connect_to_chatroom(CHANNEL_NAME) 
        print("✅ (Listener) Conectado y escuchando mensajes.")

        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ (Listener) Error principal: {e}")
    finally:
        await api.close()
        print("Bot detenido.")

# 6. Ejecuta el bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n(Listener) Saliendo...")