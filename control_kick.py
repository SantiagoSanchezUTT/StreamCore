# pruebas en consola
import sqlite3
import asyncio
import os
import sys
import threading  # Necesario para correr Twitch auth bloqueante

# --- Añade la carpeta raíz al PYTHONPATH ---
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -------------------------------------------

# --- Importa los módulos necesarios ---
from services import auth_service
from connectors import kick_connector
from event_bus import bus
from processing import chat_processor, sender_processor  # Suscripción al bus
from services import usage_kick  # Gestión de base de datos y comandos
from management import menu_kick  # Nuevo módulo de gestión
# ------------------------------------

# --- Ruta de la base de datos ---
DB_PATH = os.path.join(os.path.dirname(__file__), "database/usage_kick.db")


# ==========================================================
# UTILIDAD: USUARIOS MÁS ACTIVOS
# ==========================================================
def get_top_users(limit=10):
    """Devuelve los usuarios más activos del chat."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Si la tabla no existe aún, prevenir error
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='user_activity';
    """)
    if not cursor.fetchone():
        conn.close()
        return []

    cursor.execute("""
        SELECT username, message_count, last_message
        FROM user_activity
        ORDER BY message_count DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


# ==========================================================
# PROCESO PRINCIPAL DEL BOT DE KICK
# ==========================================================
async def run_kick_bot():
    print("🤖 Iniciando script de control para Kick...")

    # --- Inicializar y validar base de datos ---
    if not os.path.exists(DB_PATH):
        print("📂 Base de datos no encontrada. Creándola automáticamente...")
    usage_kick.init()  # ✅ Crea DB, tablas y suscribe al bus

    # --- Autenticación de Kick ---
    print("\n--- Verificando estado de Kick ---")
    auth_success_kick = False

    if auth_service.check_auth_status("kick"):
        print("✅ Kick ya está configurado.")
        auth_success_kick = True
    else:
        print("❌ Kick no está configurado. Iniciando autenticación...")
        success = await auth_service.initiate_kick_auth()
        if success:
            print("✅ Autenticación de Kick completada.")
            auth_success_kick = True
        else:
            print("❌ Falló la autenticación de Kick.")
            return  # No continuar si falla Kick

    # --- Iniciar Conector Kick ---
    if auth_success_kick:
        print("\n--- Iniciando Conector de Kick ---")
        kick_started = await kick_connector.initialize()
        if kick_started:
            print("✅ Conector de Kick iniciado y escuchando.")
        else:
            print("❌ Falló al iniciar el conector de Kick, reintentando...")
            for attempt in range(3):
                kick_started = await kick_connector.initialize()
                if kick_started:
                    print(f"✅ Conector de Kick iniciado en intento {attempt + 1}.")
                    break
                print(f"⚠️ Falló intento {attempt + 1}, reintentando en 5s...")
                await asyncio.sleep(5)
            else:
                print("🛑 No se pudo iniciar Kick después de varios intentos.")
                return
    else:
        print("🛑 No se pudo autenticar Kick.")
        return

    # --- Mostrar panel administrativo automático ---
    print("\n💡 Cargando panel de gestión automáticamente...\n")
    menu_kick.main_menu()

    # --- Mantener el bot activo ---
    print("\nBot de Kick corriendo. Presiona Ctrl+C para salir.")
    print("💡 Escribe 'menu' para abrir el panel de gestión.\n")
    try:
        while True:
            msg_input = await asyncio.to_thread(input, "> ")

            if msg_input.lower() == "quit":
                break

            elif msg_input.lower() == "menu":
                # 🧩 Abre el panel administrativo
                menu_kick.main_menu()

            elif msg_input.lower() == "top":
                users = get_top_users()
                print("\n🏆 Usuarios más activos:\n")
                if not users:
                    print("No hay actividad registrada aún.")
                else:
                    for i, (user, count, last) in enumerate(users, 1):
                        print(f"{i}. {user:<20} | {count} mensajes | Último: {last}")
                print()

            elif msg_input:
                # Envía el mensaje al bus
                bus.publish("command:reply", {"platform": "kick", "response": msg_input})

            await asyncio.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo script...")
    except asyncio.CancelledError:
        print("\n🛑 Tarea principal cancelada.")
    finally:
        # --- Limpieza ---
        print("🧹 Limpiando conector de Kick...")
        await kick_connector.shutdown()
        print("👋 ¡Adiós!")


# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================
if __name__ == "__main__":
    print("Inicializando procesadores y verificando servicios...\n")

    try:
        asyncio.run(run_kick_bot())
    except Exception as e:
        print(f"❌ Error inesperado en el script principal: {e}")