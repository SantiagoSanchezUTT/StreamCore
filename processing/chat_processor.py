from event_bus import bus
import time # Para los cooldowns
# Importamos la función que creamos en data/database.py
from data.database import get_command_for_bot 

# --- Almacenamiento en memoria para Cooldowns ---
# Estos diccionarios se reiniciarán si apagas el bot.
# Para cooldowns persistentes, necesitaríamos guardarlos en la BD.

# Rastrea el último uso GLOBAL de un comando (clave: command_name)
command_last_used = {} 
# Rastrea el último uso POR USUARIO de CUALQUIER comando (clave: sender)
user_last_used = {} 


# --- Función Helper de Permisos ---
def user_has_permission(platform: str, command_permission: str, message_data: dict) -> bool:
    """
    Comprueba si el usuario que envió el mensaje tiene el nivel
    de permiso requerido por el comando.
    """
    
    # --- Datos del usuario ---
    # Extraemos los "poderes" del usuario del mensaje original
    is_broadcaster = False
    is_moderator = False
    is_subscriber = False
    
    if platform == 'twitch':
        badges = message_data.get('tags', {}).get('badges', '')
        is_broadcaster = 'broadcaster' in badges
        is_moderator = 'moderator' in badges or is_broadcaster # El streamer es mod
        is_subscriber = 'subscriber' in badges or is_broadcaster # El streamer es sub
        
    elif platform == 'kick':
        # (Asumiendo la estructura de kickpython)
        identity = message_data.get('raw_message', {}).get('sender', {}).get('identity', {})
        is_broadcaster = identity.get('is_broadcaster', False)
        is_moderator = identity.get('is_moderator', False) or is_broadcaster
        is_subscriber = identity.get('is_subscriber', False) or is_broadcaster

    # --- Lógica de Permisos ---
    if command_permission == 'everyone':
        return True
    
    if command_permission == 'subscribers':
        # Solo subs, mods, o el streamer
        return is_subscriber or is_moderator or is_broadcaster
        
    if command_permission == 'moderators':
        # Solo mods o el streamer
        return is_moderator or is_broadcaster
        
    if command_permission == 'streamer':
        # Solo el streamer
        return is_broadcaster

    # Si el permiso no se reconoce, denegar por seguridad
    return False


# --- Procesador Principal de Mensajes ---
def process_chat_message(data: dict):
    """Escucha mensajes y decide si son comandos."""
    platform = data.get("platform")
    sender = data.get("sender")
    content = data.get("content", "").strip() 
    
    # Ignorar mensajes vacíos
    if not content:
        return
        
    command_name = content.split(' ')[0].lower() # ej: !hola

    response = None
    target_platform = platform 

    # --- LÓGICA DE COMANDOS DINÁMICOS ---
    if command_name.startswith("!"):
        
        # 1. BUSCAR EL COMANDO EN LA BD
        comando_db = get_command_for_bot(command_name)
        
        # 2. VALIDACIONES (SI NO PASA, SE IGNORA)
        if not comando_db:
            return # El comando no existe
        
        if not comando_db['active']:
            return # El comando está apagado (global)
        
        if (platform == 'twitch' and not comando_db['active_twitch']) or \
           (platform == 'kick' and not comando_db['active_kick']):
            return # El comando está apagado para esta plataforma

        # 3. VALIDACIÓN DE PERMISOS
        if not user_has_permission(platform, comando_db['permission'], data):
            print(f"Comando {command_name} denegado a {sender} (sin permisos).")
            # Opcional: enviar susurro de "No tienes permisos"
            return 

        # 4. VALIDACIÓN DE COOLDOWNS
        cooldown_seconds = comando_db['cooldown']
        current_time = time.time()
        
        # Cooldown Global (del comando)
        last_used_global = command_last_used.get(command_name, 0)
        if current_time - last_used_global < cooldown_seconds:
            print(f"Comando {command_name} en cooldown global.")
            return # Ignorar, en cooldown
            
        # Cooldown por Usuario (para evitar spam individual)
        # Puedes poner un cooldown fijo (ej. 5 seg) para cualquier comando
        user_cooldown_seconds = 5 
        last_used_by_user = user_last_used.get(sender, 0)
        if current_time - last_used_by_user < user_cooldown_seconds:
            print(f"Comando {command_name} en cooldown para {sender} (spam).")
            return # Ignorar, usuario en cooldown

        # 5. ¡VALIDACIÓN SUPERADA!
        
        # Actualizar los tiempos de cooldown
        command_last_used[command_name] = current_time
        user_last_used[sender] = current_time
        
        # Preparar la respuesta y reemplazar variables
        response = comando_db['response']
        
        if '{user}' in response:
            response = response.replace('{user}', sender)
        
        # (Aquí pondremos la lógica para {count} en el futuro)
            
    # --- Lógica de Asistencia, TTS, etc. ---
    # (Aquí va tu otra lógica, ej. log_user_assistance(...))
    # ...

    # --- ENVIAR RESPUESTA ---
    # Si encontramos una respuesta, la publicamos en el bus
    if response:
        bus.publish("command:reply", {
            "platform": target_platform,
            "response": response,
            "original_message": data 
        })

# Suscribirse al evento de mensajes recibidos
bus.subscribe("chat:message_received", process_chat_message)
print("(Chat Processor) Suscrito a eventos de chat (con DB, Permisos y Cooldowns).")