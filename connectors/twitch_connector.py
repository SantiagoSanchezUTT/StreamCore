import socket
import threading
import asyncio
from data import tokens as token_manager
from event_bus import bus
import json

# Esta clase interna manejará la conexión IRC
class _TwitchIRCBot:
    def __init__(self, username, token, channel, message_callback):
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.username = username
        self.token = f"oauth:{token}" # Twitch requiere el prefijo oauth:
        self.channel = f"#{channel}"
        
        self.sock = socket.socket()
        self.running = True
        self.message_callback = message_callback # Callback para el conector

    def connect(self):
        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS {self.token}\r\n".encode('utf-8'))
        self.sock.send(f"NICK {self.username}\r\n".encode('utf-8'))
        self.sock.send(f"JOIN {self.channel}\r\n".encode('utf-8'))
        
        # Pedimos los "Tags" (metadatos)
        self.sock.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
        print(f"(Twitch IRC) Conectado al chat de {self.channel}")

    def send_message(self, message: str):
        if not self.running: return
        try:
            self.sock.send(f"PRIVMSG {self.channel} :{message}\r\n".encode('utf-8'))
            print(f"(Twitch IRC) Mensaje enviado: {message}")
        except Exception as e:
            print(f"(Twitch IRC) Error al enviar: {e}")

    def _parse_tags(self, raw_line):
        tags_dict = {}
        if not raw_line.startswith('@'): return tags_dict
        tags_string = raw_line[1:].split(' ', 1)[0]
        for tag in tags_string.split(';'):
            try: key, value = tag.split('=', 1); tags_dict[key] = value
            except ValueError: pass
        return tags_dict

    def listen(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(2048).decode('utf-8')
                if not data: break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    
                    if line.startswith("PING"):
                        self.sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                        continue
                    
                    if "PRIVMSG" in line:
                        tags = self._parse_tags(line)
                        username = tags.get('display-name', 'Desconocido')
                        content = line.split("PRIVMSG",1)[1].split(":",1)[1]
                        
                        # Publica el mensaje usando el callback
                        self.message_callback({
                            "platform": "twitch",
                            "sender": username,
                            "content": content,
                            "raw_message": line, # Pasa la línea cruda
                            "tags": tags # Pasa los tags
                        })
                        
            except Exception as e:
                if self.running: print(f"(Twitch IRC) Error leyendo: {e}")
                break
        
        print("(Twitch IRC) Hilo de escucha detenido.")
        self.sock.close()

    def start(self):
        self.connect()
        # Iniciar la escucha en un hilo separado
        listener_thread = threading.Thread(target=self.listen, daemon=True)
        listener_thread.start()
        print("(Twitch IRC) Hilo de escucha iniciado.")
    
    def stop(self):
        self.running = False
        self.sock.close() # Cierra el socket para forzar la salida del hilo
        print("(Twitch IRC) Detenido.")

# --- Clase Conector (La que tu app ve) ---
class TwitchConnector:
    def __init__(self):
        self.bot: _TwitchIRCBot = None
        self.running = False
        
        # Suscribirse a eventos del bus (igual que Kick)
        bus.subscribe("auth:twitch_logout", self.on_logout)
        
        # !! DIFERENCIA CLAVE !!
        # El conector escucha las respuestas para ENVIARLAS
        bus.subscribe("command:reply", self.on_reply)

    def start(self):
        if self.running: return True
        print("(Twitch Connector) Iniciando...")

        tokens = token_manager.load_twitch_tokens()
        if not tokens:
            print("(Twitch Connector) Faltan tokens (twitch_tokens.json). Ejecuta el setup.")
            return False
            
        try:
            self.bot = _TwitchIRCBot(
                username=tokens["username"],
                token=tokens["access_token"],
                channel=tokens["channel"],
                message_callback=self._handle_message # Pasa la función de publicador
            )
            self.bot.start() # Inicia el bot (conexión e hilo)
            self.running = True
            
            # (Opcional) Envía un mensaje de prueba al conectar
            asyncio.create_task(self.send_test_message())
            
            return True
        except Exception as e:
            print(f"(Twitch Connector) Error al iniciar: {e}")
            self.bot = None
            self.running = False
            return False

    async def send_test_message(self):
        await asyncio.sleep(2) # Espera 2 seg
        if self.bot:
            self.bot.send_message("✅ Bot de Twitch conectado.")

    def stop(self):
        if not self.running or not self.bot: return
        print("(Twitch Connector) Deteniendo...")
        self.running = False
        try:
            self.bot.stop()
        except Exception as e:
            print(f"(Twitch Connector) Error al detener bot: {e}")
        self.bot = None
        print("(Twitch Connector) Detenido.")

    def _handle_message(self, message: dict):
        """Callback del IRC, publica en el bus."""
        print(f"(Twitch) {message['sender']}: {message['content']}")
        
        # Publica el mensaje crudo en el bus (igual que Kick)
        bus.publish("chat:message_received", message)

    # --- Manejadores de eventos del Bus ---
    def on_logout(self, data):
        """Escucha el evento de logout."""
        print("(Twitch Connector) Recibido evento de logout.")
        if self.running:
            self.stop()

    def on_reply(self, data: dict):
        """Escucha el evento de respuesta para ENVIAR."""
        if data.get("platform") != "twitch":
            return # Ignora si no es para Twitch
        
        if self.bot and self.running:
            response = data.get("response")
            if response:
                self.bot.send_message(response)
        else:
            print("(Twitch Connector) Quiso enviar respuesta pero no está conectado.")

# --- Instancia y funciones de control (igual que Kick) ---
twitch_connector_instance = TwitchConnector()

def initialize():
    if token_manager.check_tokens_exist("twitch"):
        return twitch_connector_instance.start()
    return False

def shutdown():
    twitch_connector_instance.stop()