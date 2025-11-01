import sqlite3
import os
import datetime
from event_bus import bus

# --- Ruta del archivo de base de datos ---
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/usage_kick.db")


# ==========================================================
# 🧱 INICIALIZACIÓN DE BASE DE DATOS
# ==========================================================
def init_db():
    """
    Crea la base de datos y las tablas requeridas si no existen.
    """
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        print(f"📂 Carpeta de base de datos no encontrada. Creando en: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)

    db_exists = os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not db_exists:
        print(f"🧩 Base de datos no encontrada. Creando archivo: {DB_PATH}")
    else:
        print(f"✅ Base de datos encontrada en: {DB_PATH}")

    # Tabla 1: actividad
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            platform TEXT DEFAULT 'kick',
            last_message TIMESTAMP NOT NULL,
            message_count INTEGER DEFAULT 1
        )
    """)

    # Tabla 2: asistencias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_assistance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT DEFAULT 'kick',
            username TEXT NOT NULL,
            total_asistencias INTEGER DEFAULT 1
        )
    """)

    # Tabla 3: comandos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL UNIQUE,
            response TEXT NOT NULL,
            level TEXT DEFAULT 'public',
            refresh_time INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("🗃️ Estructura de base de datos verificada correctamente.")


# ==========================================================
# 💬 ACTIVIDAD DE CHAT
# ==========================================================
def log_user_activity(username: str, platform: str = "kick"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.utcnow().isoformat()

    cursor.execute("""
        SELECT id, message_count FROM user_activity WHERE username = ? AND platform = ?
    """, (username, platform))
    record = cursor.fetchone()

    if record:
        cursor.execute("""
            UPDATE user_activity
            SET last_message = ?, message_count = ?
            WHERE id = ?
        """, (timestamp, record[1] + 1, record[0]))
    else:
        cursor.execute("""
            INSERT INTO user_activity (username, platform, last_message)
            VALUES (?, ?, ?)
        """, (username, platform, timestamp))

    conn.commit()
    conn.close()


# ==========================================================
# 🎯 REGISTRO DE ASISTENCIAS
# ==========================================================
def log_user_assistance(username: str, platform: str = "kick"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, total_asistencias FROM user_assistance WHERE username = ? AND platform = ?
    """, (username, platform))
    record = cursor.fetchone()

    if record:
        cursor.execute("""
            UPDATE user_assistance
            SET total_asistencias = ?
            WHERE id = ?
        """, (record[1] + 1, record[0]))
    else:
        cursor.execute("""
            INSERT INTO user_assistance (platform, username)
            VALUES (?, ?)
        """, (platform, username))

    conn.commit()
    conn.close()


# ==========================================================
# ⚙️ GESTIÓN DE COMANDOS
# ==========================================================
def add_command(command: str, response: str, level: str = "public", refresh_time: int = 0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO commands (command, response, level, refresh_time)
        VALUES (?, ?, ?, ?)
    """, (command.lower(), response, level, refresh_time))
    conn.commit()
    conn.close()


def get_command(command: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT response, level, refresh_time
        FROM commands
        WHERE command = ?
    """, (command.lower(),))
    result = cursor.fetchone()
    conn.close()
    return result


# ==========================================================
# 🧠 EVENT BUS AUTOMÁTICO
# ==========================================================
def on_chat_message(event_data):
    username = event_data.get("username")
    platform = event_data.get("platform", "kick")
    message = event_data.get("message", "")

    if not username:
        return

    log_user_activity(username, platform)

    if message.startswith("!"):
        command = message[1:].split()[0].lower()
        cmd_data = get_command(command)
        if cmd_data:
            response, level, refresh_time = cmd_data
            print(f"⚙️ Comando detectado: !{command} → {response}")
            bus.publish("command:reply", {"platform": platform, "response": response})


# ==========================================================
# 🚀 INICIALIZACIÓN AUTOMÁTICA
# ==========================================================
def init():
    print("🧩 Tracker de actividad y comandos cargado.")
    init_db()
    bus.subscribe("chat:message", on_chat_message)
