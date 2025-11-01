# pruebas en consola
import asyncio
import os
import sys

# --- Añade la carpeta raíz al PYTHONPATH ---
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -------------------------------------------

# --- Importa los módulos necesarios ---
from services import auth_service
from connectors import twitch_connector # <-- CAMBIO: Importa el de Twitch
from event_bus import bus
# Importa los procesadores para que se suscriban al bus
from processing import chat_processor, sender_processor 
# ------------------------------------

async def main():
    print("🤖 Iniciando script de control para Twitch...")
    auth_success_twitch = False

    # --- 1. Verificar y Autenticar TWITCH ---
    print("\n--- Verificando estado de Twitch ---")
    if auth_service.check_auth_status("twitch"):
        print("✅ Twitch ya está configurado.")
        auth_success_twitch = True
    else:
        print("❌ Twitch no está configurado. Iniciando autenticación...")
        # initiate_twitch_auth SÍ es async
        success = await auth_service.initiate_twitch_auth() 
        if success:
            print("✅ Autenticación de Twitch completada.")
            auth_success_twitch = True
        else:
            print("❌ Falló la autenticación de Twitch.")
            return

    # --- 3. Iniciar Conector ---
    twitch_started = False

    if auth_success_twitch:
        print("\n--- Iniciando Conector de Twitch ---")
        start_success = twitch_connector.initialize() 
        if start_success:
            print("✅ Conector de Twitch iniciado y escuchando.")
            twitch_started = True
        else:
            print("❌ Falló al iniciar el conector de Twitch.")

    if not twitch_started:
        print("\n🛑 El conector no pudo iniciarse. Saliendo.")
        return

    # --- 4. Mantener el script vivo ---
    print(f"\nBot (Twitch) corriendo. Presiona Ctrl+C para salir.")

    try:
        while True:
            await asyncio.sleep(1)
            # Descomenta las siguientes líneas si quieres probar a enviar mensajes
            # msg_input = await asyncio.to_thread(input, "Mensaje a Twitch (o 'quit'): ")
            # if msg_input.lower() == 'quit': break
            # if msg_input: bus.publish("command:reply", {"platform": "twitch", "response": msg_input})

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo script...")
    except asyncio.CancelledError:
         print("\n🛑 Tarea principal cancelada.")
    finally:
        # --- 5. Limpieza ---
        print("🧹 Limpiando conectores...")
        if twitch_started:
            print("   - Deteniendo Twitch...")
            # shutdown() de Twitch también es SÍNCRONO
            twitch_connector.shutdown()

        print("👋 ¡Adiós!")


if __name__ == "__main__":
    print("Inicializando procesadores (suscribiéndose al bus)...")
    _ = chat_processor
    _ = sender_processor

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error inesperado en el script principal: {e}")