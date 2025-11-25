CONFIG = {
    "enabled": True,

    # Solo leer si escriben !tts
    "command_mode": False,

    # Reglas anti-spam
    "cooldown_seconds": 4,
    "max_length": 200,
    "per_user_limit": 3,
    "filter_bad_words": True,

    "banned_words": [
        "porno", "xxx", "nsfw", "racist", "nazi"
    ],

    # Plataformas
    "read_kick": True,
    "read_twitch": True,

    # Solo subs
    "only_subscribers": False,
}