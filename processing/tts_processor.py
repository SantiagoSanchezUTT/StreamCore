import time
from processing.tts_config import CONFIG

class ChatProcessor:
    def __init__(self, tts):
        self.tts = tts
        self.user_times = {}

    def process_message(self, username, message, is_sub=False):
        if not CONFIG["enabled"]:
            return

        # Solo subs
        if CONFIG["only_subscribers"] and not is_sub:
            return

        # Modo comando
        if CONFIG["command_mode"]:
            if not message.lower().startswith("!tts"):
                return
            message = message[4:].strip()

        # Palabras prohibidas
        if CONFIG["filter_bad_words"]:
            msg_l = message.lower()
            for b in CONFIG["banned_words"]:
                if b in msg_l:
                    print(f"⛔ Bloqueado por palabra prohibida: {b}")
                    return

        # Longitud
        if len(message) > CONFIG["max_length"]:
            print("⛔ Mensaje demasiado largo")
            return

        # Anti-spam por usuario
        now = time.time()
        user_list = self.user_times.get(username, [])
        user_list = [t for t in user_list if now - t < 60]

        if len(user_list) >= CONFIG["per_user_limit"]:
            print("⛔ Usuario excedió mensajes por minuto")
            return

        user_list.append(now)
        self.user_times[username] = user_list

        # Cooldown global
        if hasattr(self, "_last_time") and now - self._last_time < CONFIG["cooldown_seconds"]:
            print("⛔ Cooldown global activo")
            return

        self._last_time = now

        # Ejecutar
        self.tts.speak(f"{username} dice: {message}")