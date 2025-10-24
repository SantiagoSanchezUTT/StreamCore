# Guarda esto en: streamcore/api.py
import subprocess
import os
import json

# --- ¡CAMBIO AQUÍ! ---
# La carpeta del bot ahora se llama 'kick'
BASE_DIR = os.path.dirname(__file__)
BOT_DIR = os.path.join(os.path.dirname(__file__), 'kick')
TWITCH_BOT_DIR = os.path.join(BASE_DIR, 'twitch_bot')
# --------------------

class Api:
    def __init__(self):
        self._listener_process = None # Para guardar el proceso del bot de Kick
        self._twitch_process = None # Para guardar el proceso del bot de Twitch

    def check_setup_status(self):
        """Revisa si el bot ya fue configurado."""
        config_path = os.path.join(BOT_DIR, 'config.json')
        tokens_path = os.path.join(BOT_DIR, 'kick_tokens.db')
        
        if os.path.exists(config_path) and os.path.exists(tokens_path):
            print("(API) Estado: Configurado.")
            return {"status": "configured"}
        else:
            print("(API) Estado: No configurado.")
            return {"status": "unconfigured"}

    def run_kick_setup(self):
        """Llama a 'setup.py' para que el usuario se loguee."""
        setup_script_path = os.path.join(BOT_DIR, 'setup.py')
        print(f"(API) Ejecutando setup: {setup_script_path}")
        
        try:
            # Ejecuta setup.py en un nuevo proceso
            subprocess.Popen(['py', setup_script_path], cwd=BOT_DIR)
            return {"success": True, "message": "Proceso de setup iniciado."}
        except Exception as e:
            print(f"(API) Error al iniciar setup: {e}")
            return {"success": False, "message": str(e)}

    def start_kick_bot(self):
        """Inicia el 'listener.py' en un proceso separado."""
        if self._listener_process and self._listener_process.poll() is None:
            print("(API) El bot ya está corriendo.")
            return {"success": False, "message": "El bot ya está corriendo."}

        listener_script_path = os.path.join(BOT_DIR, 'listener.py')
        print(f"(API) Iniciando bot: {listener_script_path}")
        
        try:
            # Inicia el listener y guarda el proceso
            self._listener_process = subprocess.Popen(
                ['py', listener_script_path], 
                cwd=BOT_DIR
            )
            print(f"(API) Bot iniciado (PID: {self._listener_process.pid}).")
            return {"success": True, "message": "Bot iniciado."}
        except Exception as e:
            print(f"(API) Error al iniciar bot: {e}")
            return {"success": False, "message": str(e)}

    def stop_kick_bot(self):
        """Detiene el proceso del 'listener.py'."""
        if self._listener_process and self._listener_process.poll() is None:
            print(f"(API) Deteniendo bot (PID: {self._listener_process.pid})...")
            self._listener_process.terminate() # Termina el proceso
            self._listener_process = None
            print("(API) Bot detenido.")
            return {"success": True, "message": "Bot detenido."}
        else:
            print("(API) El bot no estaba corriendo.")
            return {"success": False, "message": "El bot no estaba corriendo."}
        
    def check_twitch_setup_status(self):
        """Revisa si ya existen tokens de Twitch guardados."""
        tokens_path = os.path.join(TWITCH_BOT_DIR, 'twitch_tokens.json')
        if os.path.exists(tokens_path):
            return {"status": "configured"}
        return {"status": "unconfigured"}

    def start_twitch_bot(self):
        """
        Ejecuta el script de Twitch. 
        Este script maneja su propia autenticación si es necesario.
        """
        if self._twitch_process and self._twitch_process.poll() is None:
            return {"success": False, "message": "Bot de Twitch ya está corriendo."}
            
        script_path = os.path.join(TWITCH_BOT_DIR, 'twitch.py')
        print(f"(API) Iniciando bot de Twitch: {script_path}")
        try:
            self._twitch_process = subprocess.Popen(['py', script_path], cwd=TWITCH_BOT_DIR)
            return {"success": True, "message": "Bot de Twitch iniciado."}
        except Exception as e:
            print(f"(API) Error al iniciar bot de Twitch: {e}")
            return {"success": False, "message": str(e)}

    def stop_twitch_bot(self):
        """Detiene el proceso del 'twitch.py'."""
        if self._twitch_process and self._twitch_process.poll() is None:
            print(f"(API) Deteniendo bot de Twitch (PID: {self._twitch_process.pid})...")
            self._twitch_process.terminate()
            self._twitch_process = None
            print("(API) Bot de Twitch detenido.")
            return {"success": True, "message": "Bot de Twitch detenido."}
        return {"success": False, "message": "Bot de Twitch no estaba corriendo."}