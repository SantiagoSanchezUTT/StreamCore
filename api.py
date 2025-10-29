# Guarda esto en: api.py
import asyncio
import threading
import os
# Importa los módulos necesarios
from services import auth_service
from data import tokens as token_manager # Puede ser útil para alguna verificación extra
# from data.utils import get_persistent_data_path # Ya no es necesario aquí directamente
from event_bus import bus # Para publicar eventos si es necesario

class Api:
    def __init__(self):
        print("(API) Instancia creada.")
        pass

    # --- Funciones de Estado y Autenticación ---

    def check_auth_status(self, platform):
        """
        Revisa si una plataforma ya tiene tokens guardados.
        Llama directamente a la función del auth_service.
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
                # auth_service ya publica el evento 'auth:kick_completed' en el bus principal
            except Exception as e:
                print(f"(API) Error en hilo auth Kick: {e}")
                # Publica el error en el bus principal si falla el hilo
                bus.publish("auth:kick_completed", {"success": False, "error": str(e)})

        thread = threading.Thread(target=auth_thread_func, daemon=True)
        thread.start()
        # Devuelve inmediatamente a la UI
        return {"success": True, "message": "Proceso de autenticación de Kick iniciado en segundo plano."}

#    def run_twitch_auth(self):
        """
        Inicia el flujo de autenticación de Twitch en un hilo separado.
        (Llamada desde la UI)
        """
        print("(API) Solicitando autenticación de Twitch (en hilo)...")

        def auth_thread_func():
            print("(API) Hilo de autenticación Twitch iniciado.")
            try:
                success = auth_service.initiate_twitch_auth()
                print(f"(API) Resultado auth Twitch (hilo finalizado): {success}")
            except Exception as e:
                print(f"(API) Error en hilo auth Twitch: {e}")
                # Publica el error en el bus principal si falla el hilo
                bus.publish("auth:twitch_completed", {"success": False, "error": str(e)})

        thread = threading.Thread(target=auth_thread_func, daemon=True)
        thread.start()
        # Devuelve inmediatamente a la UI
        return {"success": True, "message": "Proceso de autenticación de Twitch iniciado en segundo plano."}
#
    def run_logout(self, platform):
        """
        Llama al servicio para desvincular una cuenta (borrar tokens).
        (Llamada desde la UI)
        """
        print(f"(API) Solicitando desvinculación de {platform}...")
        # auth_service.logout publica el evento 'auth:{platform}_logout'
        success = auth_service.logout(platform)
        return {"success": success, "message": f"Desvinculación de {platform} {'exitosa' if success else 'fallida'}."}