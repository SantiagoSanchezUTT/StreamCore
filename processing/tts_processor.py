import time
from tts_config import CONFIG

class ChatProcessor:
    def __init__(self, tts_engine):
        self.tts = tts_engine
        self.last_global_tts = 0
        self.user_last_tts = {}

    # ==========================================
    def is_tts_command(self, msg: str):
        parts = msg.strip().split(" ", 1)
        cmd = parts[0].lower()
        return cmd in CONFIG["tts_commands"]

    # ==========================================
    def check_cooldowns(self, username):
        now = time.time()

        # Cooldown global
        if now - self.last_global_tts < CONFIG["global_cooldown"]:
            return False, f"⏳ Cooldown global: espera {CONFIG['global_cooldown']}s."

        # Cooldown por usuario
        if username in self.user_last_tts:
            if now - self.user_last_tts[username] < CONFIG["user_cooldown"]:
                return False, f"⏳ {username}, espera {CONFIG['user_cooldown']}s"

        return True, None

    # ==========================================
    def process_message(self, username, message):
        msg = message.strip()

        if not self.is_tts_command(msg):
            return False

        # Extraer texto
        parts = msg.split(" ", 1)
        if len(parts) == 1:
            print("⚠️ Comando TTS sin mensaje.")
            return False

        text = parts[1].strip()

        # Validar longitud
        if len(text) > CONFIG["max_chars"]:
            print("❌ Mensaje demasiado largo.")
            return False

        # Cooldowns
        ok, reason = self.check_cooldowns(username)
        if not ok:
            print(reason)
            return False

        # Registrar cooldowns
        now = time.time()
        self.last_global_tts = now
        self.user_last_tts[username] = now

        # Ejecutar TTS
        print(f"🔊 [TTS] {username}: {text}")
        self.tts.speak(text)

        return True