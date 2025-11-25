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
from processing.tts_handler import tts_handler

# --------------------------------

# --- Define rutas ---
script_dir = pathlib.Path(__file__).parent.resolve()
html_path = script_dir / 'web' / 'streamcore_config.html'
html_file_abs_path = str(html_path)
# --------------------

# --- RE-AÑADIMOS LA LÓGICA DE ARRANQUE ---
# Esta vez, se ejecutará al inicio SI los tokens ya existen.
async def start_connectors_async():
    """Intenta inicializar los conectores si están autenticados."""
    print("Verificando conectores en segundo plano...")
    tasks = []
    
    if auth_service.check_auth_status("kick"):
        print("   - Kick está configurado. Intentando iniciar...")
        # Usamos la instancia directamente
        tasks.append(asyncio.create_task(kick_connector.kick_connector_instance.start()))
    else:
        print("   - Kick no configurado, omitiendo inicio.")

    if auth_service.check_auth_status("twitch"):
        print("   - Twitch está configurado. Intentando iniciar...")
        loop = asyncio.get_running_loop()
        # Usamos la instancia directamente
        tasks.append(loop.run_in_executor(None, twitch_connector.twitch_connector_instance.start))
    else:
        print("   - Twitch no configurado, omitiendo inicio.")

    if tasks:
        await asyncio.gather(*tasks)
    print("🏁 Verificación de conectores completada.")

def run_async_connectors_in_thread():
    """Wrapper para correr el chequeo inicial en un hilo."""
    print("Creando hilo para chequeo inicial de conectores...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_connectors_async())
    except Exception as e:
        print(f"Error en el hilo de conectores: {e}")
    finally:
        print("Hilo de chequeo de conectores finalizado.")
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

    # --- HILO RE-AÑADIDO ---
    # Este hilo correrá UNA VEZ al inicio para conectar
    # los servicios que ya están autenticados.
    print("   - Creando hilo para chequeo inicial de conectores...")
    connector_thread = threading.Thread(target=run_async_connectors_in_thread, daemon=True)
    connector_thread.start()
    
    print("Iniciando interfaz gráfica...")
    webview.start(debug=True)

    # --- Lógica de apagado (Sin cambios) ---
    shutdown_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(shutdown_loop)
    try:
        print("   - Solicitando detención de Kick...")
        shutdown_loop.run_until_complete(kick_connector.shutdown())
    except Exception as e: print(f"   - Error deteniendo Kick: {e}")

    try:
        print("   - Solicitando detención de Twitch...")
        twitch_connector.shutdown()
    except Exception as e: print(f"   - Error deteniendo Twitch: {e}")

    print("\nAplicación cerrada. Deteniendo componentes...")
    shutdown_loop.close()

    print("¡Adiós!")