CONFIG = {
    # ==========================================
    # 🎛️ AUDIO Y VOZ (Lo que requiere tts_engine)
    # ==========================================
    "enabled": True,             # Interruptor general
    "volume": 1.0,               # Volumen (0.0 a 1.0)
    "speed": 200,                # Velocidad de lectura (Rate)
    "pitch": 0,                  # Tono de voz (-20 a 20 aprox)
    "voice": "",                 # ID de la voz (vacío = default)
    
    # Este es el que te dio error recién. 
    # Usualmente define si usa motor "local", "cloud" o una estrategia de lectura.
    "voice_mode": "standard",    
    
    # Para seleccionar parlantes/audífonos (está en tu HTML)
    "output_device": 0,          # Índice del dispositivo de audio (0 = default)

    # ==========================================
    # 🧠 LÓGICA Y FILTROS
    # ==========================================
    "command_mode": False,       # ¿Leer solo con !tts?
    "ignore_commands": True,     # Ignorar mensajes que empiecen con ! o /
    "max_length": 200,           # Cortar mensajes muy largos
    
    # Filtros de audiencia (basado en tu HTML)
    "only_subscribers": False,   # Solo leer subs
    "only_followers": False,     # Solo leer seguidores
    
    # ==========================================
    # 🛡️ SEGURIDAD Y ANTI-SPAM
    # ==========================================
    "cooldown_seconds": 4,       # Espera entre mensajes
    "per_user_limit": 3,         # Límite de mensajes seguidos por usuario
    "filter_bad_words": True,    # Censurar groserías
    "banned_words": [
        "porno", "xxx", "nsfw", "racist", "nazi", "banword"
    ],

    # ==========================================
    # 🌐 PLATAFORMAS
    # ==========================================
    "read_twitch": True,
    "read_kick": True,
    "read_youtube": False,
}