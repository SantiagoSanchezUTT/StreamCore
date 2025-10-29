from event_bus import bus

def process_chat_message(data: dict):
    """Escucha mensajes y decide si son comandos."""
    platform = data.get("platform")
    sender = data.get("sender")
    content = data.get("content", "").strip().lower()

    print(f"(Chat Processor) Procesando mensaje de {platform}: '{content}'")

    response = None
    target_platform = platform # Por defecto, responde en la misma plataforma

    # --- Lógica de Comandos ---
    if content == "!ping":
        response = "¡pong!"
    elif content == "!hola":
        response = f"¡Hola {sender}! 👋"
    elif content == "!redes":
        response = "¡Sígueme en mis redes! www.ejemplo.com"

    # --- Lógica de Asistencia, TTS, etc. ---
    # Aquí podrías llamar a attendance_service.log_user(platform, sender)
    # O si el mensaje activa TTS, llamar a tts_service.add_to_queue(platform, content)
    # y esos servicios podrían publicar sus propios eventos si necesitan respuesta.

    # Si hubo una respuesta de comando, publicarla
    if response:
        bus.publish("command:reply", {
            "platform": target_platform,
            "response": response,
            "original_message": data # Pasa el mensaje original por si se necesita contexto
        })

# Suscribirse al evento de mensajes recibidos
bus.subscribe("chat:message_received", process_chat_message)
print("(Chat Processor) Suscrito a eventos de chat.")