from processing.tts_engine import OfflineTTS
from processing.tts_processor import ChatProcessor
from processing.tts_config import CONFIG
from event_bus import bus


class TTSHandler:
    def __init__(self):
        print("🔊 Inicializando TTS automático basado en chat...")

        self.tts = OfflineTTS()
        self.processor = ChatProcessor(self.tts)

        # Conexión al flujo de mensajes
        if CONFIG["read_kick"]:
            bus.subscribe("kick:message", self.on_kick)

        if CONFIG["read_twitch"]:
            bus.subscribe("twitch:message", self.on_twitch)

        print("✅ TTS ahora escucha los eventos del chat.\n")

    # --- Mensaje de Kick ---
    def on_kick(self, data):
        username = data.get("username")
        message = data.get("message")
        is_sub = data.get("is_subscriber", False)

        if username and message:
            self.processor.process_message(username, message, is_sub)

    # --- Mensaje de Twitch ---
    def on_twitch(self, data):
        username = data.get("username")
        message = data.get("message")
        is_sub = data.get("is_subscriber", False)

        if username and message:
            self.processor.process_message(username, message, is_sub)


# Instancia global automática
tts_handler = TTSHandler()
