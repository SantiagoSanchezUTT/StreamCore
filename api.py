# En: src/api.py
import asyncio
import threading
import os
# --- IMPORTACIONES MODIFICADAS ---
from services import auth_service
from data import tokens as token_manager # Importamos el token_manager
from event_bus import bus

class Api:
    def __init__(self):
        print("(API) Instancia creada.")
        pass

    # --- ¡NUEVA FUNCIÓN! ---
    def get_all_auth_status(self):
        """
        Revisa el estado de TODAS las plataformas y devuelve los datos
        del perfil si están conectadas.
        Llamada por el JS al cargar la página.
        """
        print("(API) Solicitando estado de autenticación de todas las plataformas...")
        status = {
            "twitch": {"status": "disconnected"},
            "kick": {"status": "disconnected"}
        }

        # 1. Revisar Twitch
        if token_manager.check_tokens_exist("twitch"):
            data = token_manager.load_twitch_tokens()
            if data:
                status["twitch"] = {
                    "status": "connected",
                    "username": data.get("username", "Usuario Twitch"),
                    "profile_pic": data.get("profile_image_url", "")
                }
        
        # 2. Revisar Kick
        if token_manager.check_tokens_exist("kick"):
            data = token_manager.load_kick_config()
            if data:
                status["kick"] = {
                    "status": "connected",
                    "username": data.get("CHANNEL_NAME", "Usuario Kick"),
                    "profile_pic": data.get("profile_image_url", "")
                }
        
        print(f"(API) Estado de autenticación: {status}")
        return status

    # --- Funciones de Estado y Autenticación (Sin cambios, pero con imports corregidos) ---

    def check_auth_status(self, platform):
        """
        Revisa si una plataforma ya tiene tokens guardados.
        (Esta función ya no es necesaria para la UI principal, pero la dejamos)
        """
        is_connected = auth_service.check_auth_status(platform)
        status = "connected" if is_connected else "disconnected"
        print(f"(API) Estado de {platform}: {status}")
        return {"platform": platform, "status": status}

    async def run_kick_auth_async(self):
        """Función async interna para Kick auth (necesaria para correr en hilo)."""
        print("(API) Iniciando llamada async a initiate_kick_auth...")
        return await auth_service.initiate_kick_auth()

    def run_kick_auth(self):
        """
        Inicia el flujo de autenticación de Kick en un hilo separado.
        (Llamada desde la UI)
        """
        print("(API) Solicitando autenticación de Kick (en hilo)...")

        def auth_thread_func():
            print("(API) Hilo de autenticación Kick iniciado.")
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self.run_kick_auth_async())
                loop.close()
                print(f"(API) Resultado auth Kick (hilo finalizado): {success}")
                # Publicamos en el bus para que el frontend (JS) pueda escuchar
                bus.publish("auth:kick_completed", {"success": success})
            except Exception as e:
                print(f"(API) Error en hilo auth Kick: {e}")
                bus.publish("auth:kick_completed", {"success": False, "error": str(e)})

        thread = threading.Thread(target=auth_thread_func, daemon=True)
        thread.start()
        return {"success": True, "message": "Proceso de autenticación de Kick iniciado en segundo plano."}

    async def run_twitch_auth_async(self):
        """Función async interna para Twitch auth."""
        print("(API) Iniciando llamada async a initiate_twitch_auth...")
        return await auth_service.initiate_twitch_auth()

    def run_twitch_auth(self):
        """
        Inicia el flujo de autenticación de Twitch en un hilo separado.
        (Llamada desde la UI)
        """
        print("(API) Solicitando autenticación de Twitch (en hilo)...")

        def auth_thread_func():
            print("(API) Hilo de autenticación Twitch iniciado.")
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self.run_twitch_auth_async())
                loop.close()
                print(f"(API) Resultado auth Twitch (hilo finalizado): {success}")
                # Publicamos en el bus para que el frontend (JS) pueda escuchar
                bus.publish("auth:twitch_completed", {"success": success})
            except Exception as e:
                print(f"(API) Error en hilo auth Twitch: {e}")
                bus.publish("auth:twitch_completed", {"success": False, "error": str(e)})

        thread = threading.Thread(target=auth_thread_func, daemon=True)
        thread.start()
        return {"success": True, "message": "Proceso de autenticación de Twitch iniciado en segundo plano."}
    
    def run_logout(self, platform):
        """
        Llama al servicio para desvincular una cuenta (borrar tokens).
        (Llamada desde la UI)
        """
        print(f"(API) Solicitando desvinculación de {platform}...")
        success = auth_service.logout(platform)
        
        # Publicamos el evento para que el JS actualice la UI
        bus.publish(f"auth:{platform}_logout", {"success": success})
        
        return {"success": success, "message": f"Desvinculación de {platform} {'exitosa' if success else 'fallida'}."}