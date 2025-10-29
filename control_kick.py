# pruebas en consola
import asyncio
import os
import sys
import threading # Necesario para correr Twitch auth bloqueante

# --- Añade la carpeta raíz al PYTHONPATH ---
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -------------------------------------------

# --- Importa los módulos necesarios ---
from services import auth_service
from connectors import kick_connector
from event_bus import bus
from processing import chat_processor, sender_processor # Asegura que se importen
# ------------------------------------

async def main():
    print("🤖 Iniciando script de control para Kick y Twitch...")
    auth_success_kick = False

    # --- 1. Verificar y Autenticar KICK ---
    print("\n--- Verificando estado de Kick ---")
    if auth_service.check_auth_status("kick"):
        print("✅ Kick ya está configurado.")
        auth_success_kick = True
    else:
        print("❌ Kick no está configurado. Iniciando autenticación...")
        success = await auth_service.initiate_kick_auth() # Es async
        if success:
            print("✅ Autenticación de Kick completada.")
            auth_success_kick = True
        else:
            print("❌ Falló la autenticación de Kick.")
            # Puedes decidir si continuar sin Kick o salir
            # return

    # --- 3. Iniciar Conectores ---
    kick_started = False
    twitch_started = False

    if auth_success_kick:
        print("\n--- Iniciando Conector de Kick ---")
        start_success = await kick_connector.initialize()
        if start_success:
            print("✅ Conector de Kick iniciado y escuchando.")
            kick_started = True
        else:
            print("❌ Falló al iniciar el conector de Kick.")

    if not kick_started and not twitch_started:
        print("\n🛑 Ningún conector pudo iniciarse. Saliendo.")
        return

    # --- 4. Mantener el script vivo ---
    platforms_running = []
    if kick_started: platforms_running.append("Kick")
    if twitch_started: platforms_running.append("Twitch")
    print(f"\nBot(s) ({', '.join(platforms_running)}) corriendo. Presiona Ctrl+C para salir.")

    try:
        while True:
            await asyncio.sleep(1)
            # Puedes añadir lógica para enviar mensajes aquí si quieres
            # msg_input = await asyncio.to_thread(input, "Mensaje a Kick (o 'quit'): ")
            # if msg_input.lower() == 'quit': break
            # if msg_input: bus.publish("command:reply", {"platform": "kick", "response": msg_input})

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo script...")
    except asyncio.CancelledError:
         print("\n🛑 Tarea principal cancelada.") # Manejo por si acaso
    finally:
        # --- 5. Limpieza ---
        print("🧹 Limpiando conectores...")
        if kick_started:
            print("   - Deteniendo Kick...")
            await kick_connector.shutdown()
        if twitch_started:
            print("   - Deteniendo Twitch...")
            # La función shutdown de Twitch es síncrona
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(None, twitch_connector.shutdown)
            except Exception as e:
                print(f"   - Error al detener Twitch: {e}")

        print("👋 ¡Adiós!")


if __name__ == "__main__":
    print("Inicializando procesadores (suscribiéndose al bus)...")
    # Importar los procesadores asegura que sus suscripciones al bus se ejecuten

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error inesperado en el script principal: {e}")