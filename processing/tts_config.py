# ==========================================
# CONFIGURACIÓN GENERAL PARA EL TTS
# ==========================================

CONFIG = {
    "voice_mode": "any",      # single / male / female / any
    "voice_index": None,      # solo si voice_mode = "single"
    "speed": 170,
    "volume": 1.0,
    "pitch": 80,

    # Comandos TTS permitidos
    "tts_commands": ["!tts", "!habla", "!voz"],

    # Máximo de caracteres permitidos por mensaje
    "max_chars": 300,

    # Cooldown global (segundos entre mensajes TTS)
    "global_cooldown": 2,

    # Cooldown por usuario
    "user_cooldown": 10,

    # Prefijo de comando
    "command_prefix": "!"
}