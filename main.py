import webview
import os
import pathlib
import threading
import asyncio
from api import Api
from event_bus import bus
from connectors import kick_connector
from processing import chat_processor, sender_processor
from services import auth_service
from connectors import twitch_connector
# --------------------------------

# --- Define rutas ---
script_dir = pathlib.Path(__file__).parent.resolve()
html_path = script_dir / 'web' / 'streamcore_config.html'
html_file_abs_path = str(html_path)
# --------------------

# --- Función para iniciar conectores en segundo plano ---
async def start_connectors_async():
    """Intenta inicializar los conectores si están autenticados."""
    print("Iniciando conectores en segundo plano...")
    tasks = []
    
    # Lógica de Kick (sin cambios)
    if auth_service.check_auth_status("kick"):
        print("   - Intentando iniciar Kick...")
        tasks.append(asyncio.create_task(kick_connector.initialize()))
    else:
        print("   - Kick no configurado, omitiendo inicio.")

    # --- AÑADIR LÓGICA DE TWITCH ---
    if auth_service.check_auth_status("twitch"):
        print("   - Intentando iniciar Twitch...")
        # initialize() de Twitch NO es async, lo llamamos en un hilo de executor
        loop = asyncio.get_running_loop()
        # run_in_executor envuelve la llamada síncrona en una tarea async
        tasks.append(loop.run_in_executor(None, twitch_connector.initialize))
    else:
        print("   - Twitch no configurado, omitiendo inicio.")
    # --- FIN DEL CAMBIO ---

    if tasks:
        await asyncio.gather(*tasks)
    print("🏁 Iniciación de conectores completada.")

def run_async_connectors_in_thread():
    """Wrapper para correr start_connectors_async en un hilo con su propio bucle."""
    print("Creando hilo para conectores...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_connectors_async())
    except Exception as e:
        print(f"Error en el hilo de conectores: {e}")
    finally:
        print("Hilo de conectores finalizado.")
# --------------------------------------------------------

if __name__ == '__main__':
    print("Iniciando StreamCore...")
    print("   - Inicializando procesadores (suscribiéndose)...")
    _ = chat_processor
    _ = sender_processor

    api_instance = Api()

    # Crea la ventana
    window = webview.create_window(
        'StreamCore',
        html_file_abs_path,
        js_api=api_instance,
        width=1280,
        height=720
    )

    print("   - Creando hilo para iniciar conectores...")
    connector_thread = threading.Thread(target=run_async_connectors_in_thread, daemon=True)
    connector_thread.start()
    
    print("Iniciando interfaz gráfica...")
    webview.start(debug=True)

    shutdown_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(shutdown_loop)
    try:
        print("   - Solicitando detención de Kick...")
        shutdown_loop.run_until_complete(kick_connector.shutdown())
    except Exception as e: print(f"   - Error deteniendo Kick: {e}")

    # --- AÑADIR LÓGICA DE TWITCH ---
    try:
        print("   - Solicitando detención de Twitch...")
        # shutdown() de Twitch NO es async, se llama directamente
        twitch_connector.shutdown()
    except Exception as e: print(f"   - Error deteniendo Twitch: {e}")
    # --- FIN DEL CAMBIO ---

    print("\nAplicación cerrada. Deteniendo componentes...")
    # Cierra el bucle de limpieza
    shutdown_loop.close()

    print("¡Adiós!")