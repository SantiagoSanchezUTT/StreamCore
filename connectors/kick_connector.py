import asyncio
from kickpython import KickAPI
from data import tokens as token_manager
from event_bus import bus
import json
from dotenv import load_dotenv
import os


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
KICK_CLIENT_ID = os.getenv("KICK_CLIENT_ID")
KICK_CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")

class KickConnector:
    def __init__(self):
        self.api = None
        self.channel_name = None
        self.running = False

    async def start(self):
        if self.running: return True
        print("(Kick Connector) Iniciando...")

        config = token_manager.load_kick_config()
        if not config or 'CHANNEL_NAME' not in config:
            print("(Kick Connector) Falta configuración (config.json). Ejecuta el setup.")
            return False
        self.channel_name = config['CHANNEL_NAME']
        
        try:
            self.api = KickAPI(
                 client_id=KICK_CLIENT_ID,
                 client_secret=KICK_CLIENT_SECRET,
                 db_path=token_manager.KICK_DB_PATH # Usa la ruta persistente
            )
            # Registra el handler ANTES de conectar
            self.api.add_message_handler(self._handle_message)
            print("(Kick Connector) Controlador de mensajes registrado.")
            
            # Inicia el refresco automático (si es necesario)
            await self.api.start_token_refresh()

            print(f"(Kick Connector) Conectando al chatroom de {self.channel_name}...")
            await self.api.connect_to_chatroom(self.channel_name)
            print("(Kick Connector) Conectado y escuchando.")
            self.running = True
            return True
        except Exception as e:
            print(f"(Kick Connector) Error al iniciar o conectar: {e}")
            if self.api: await self.api.close()
            self.api = None
            self.running = False
            return False

    async def stop(self):
        if not self.running or not self.api: return
        print("(Kick Connector) Deteniendo...")
        self.running = False
        try:
            await self.api.close()
        except Exception as e:
            print(f"(Kick Connector) Error al cerrar API: {e}")
        self.api = None
        print("(Kick Connector) Detenido.")

    async def _handle_message(self, message: dict):
        """Callback de kickpython, publica en el bus."""
        content = message.get('content', '')
        sender = message.get('sender_username', 'Desconocido')
        
        print(f"(Kick) {sender}: {content}")

        # Publica el mensaje crudo en el bus
        bus.publish("chat:message_received", {
            "platform": "kick",
            "sender": sender,
            "content": content,
            "raw_message": message # Pasa el diccionario completo
        })

# --- Instancia y funciones de control ---
kick_connector_instance = KickConnector()

async def initialize():
    # Intenta iniciar automáticamente si está configurado
    if token_manager.check_tokens_exist("kick"):
        await kick_connector_instance.start()

async def shutdown():
    await kick_connector_instance.stop()

# --- Suscripción a eventos del bus ---
def on_kick_logout(data):
    """Escucha el evento de logout para detener el conector."""
    print("(Kick Connector) Recibido evento de logout.")
    # Usamos asyncio.create_task para llamar a la función async stop
    if kick_connector_instance.running:
        asyncio.create_task(kick_connector_instance.stop())

bus.subscribe("auth:kick_logout", on_kick_logout)