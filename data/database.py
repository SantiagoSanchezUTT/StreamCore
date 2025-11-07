import sqlite3
import os # Necesitamos 'os' para crear directorios
from .utils import get_persistent_data_path 

APP_DATA_ROOT = os.path.dirname(get_persistent_data_path("dummy.txt"))

# Creamos la ruta a nuestra carpeta "bd"
DB_DIR = os.path.join(APP_DATA_ROOT, "bd")

# Aseguramos que el directorio "bd" exista
os.makedirs(DB_DIR, exist_ok=True)

# Creamos la ruta final al archivo de la base de datos
DB_PATH = os.path.join(DB_DIR, "streamcore.db")

print(f"Base de datos unificada en: {DB_PATH}")


# --- 2. CONEXIÓN ---
def get_connection():
    """Conexión simple. Usada por funciones que no devuelven filas."""
    return sqlite3.connect(DB_PATH)

def get_db_conn_dict():
    """Conexión que devuelve diccionarios. Usada por funciones 'get'."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- 3. INICIALIZACIÓN (Tablas fusionadas) ---
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabla 1: Asistencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                nickname TEXT NOT NULL,
                total_asistencias INTEGER DEFAULT 1,
                UNIQUE(nickname, platform)
            )
        """)

        # Tabla 2: Comandos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comandos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,          -- ej: !social
                type TEXT NOT NULL,                 -- ej: text, counter
                response TEXT NOT NULL,
                cooldown INTEGER DEFAULT 5,
                permission TEXT DEFAULT 'everyone', -- ej: everyone, mods
                active BOOLEAN DEFAULT 1,           -- Toggle global
                uses INTEGER DEFAULT 0,
                active_twitch BOOLEAN DEFAULT 1,    -- Toggle Twitch
                active_kick BOOLEAN DEFAULT 1       -- Toggle Kick
            )
        """)
        
        conn.commit()
    print("Tablas de Base de Datos (Asistencias y Comandos) aseguradas.")


# --- 4. FUNCIONES CRUD ---

# --- Funciones de Asistencia (Tu lógica original, sin cambios) ---
def log_user_assistance(nickname: str, platform: str):
    """
    Registra una asistencia. Si el usuario ya existe, incrementa
    el total. Si no, lo crea con 1 asistencia.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO asistencias (nickname, platform, total_asistencias)
            VALUES (?, ?, 1)
            ON CONFLICT(nickname, platform) DO UPDATE SET
                total_asistencias = total_asistencias + 1
        """, (nickname.lower(), platform.lower()))
        conn.commit()

def get_all_asistencias():
    """Obtiene la lista de todas las asistencias, ordenadas."""
    # Usamos la conexión que devuelve diccionarios
    with get_db_conn_dict() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, platform, nickname, total_asistencias 
            FROM asistencias ORDER BY total_asistencias DESC
        """)
        # Devolvemos una lista de diccionarios
        return [dict(row) for row in cursor.fetchall()]

# --- Funciones de Comandos (¡NUEVA LÓGICA PARA LA UI!) ---
# Estas reemplazan tus antiguas 'add_command', 'get_command', etc.

def get_commands():
    """READ: Obtiene todos los comandos para la UI."""
    with get_db_conn_dict() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comandos ORDER BY name ASC")
        commands = [dict(row) for row in cursor.fetchall()]
        return commands

def create_command(data):
    """CREATE: Añade un nuevo comando desde la UI."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO comandos 
                   (name, type, response, cooldown, permission, active, 
                    active_twitch, active_kick) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['name'], data['type'], data['response'], data['cooldown'],
                    data['permission'], data['active'],
                    data['active_twitch'], data['active_kick']
                )
            )
            conn.commit()
            new_id = cursor.lastrowid
            return {"success": True, "id": new_id}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "El nombre del comando ya existe"}

def update_command(command_id, data):
    """UPDATE: Actualiza un comando existente desde la UI."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE comandos SET 
                   name = ?, type = ?, response = ?, cooldown = ?, 
                   permission = ?, active = ?,
                   active_twitch = ?, active_kick = ?
                   WHERE id = ?""",
                (
                    data['name'], data['type'], data['response'], data['cooldown'],
                    data['permission'], data['active'],
                    data['active_twitch'], data['active_kick'],
                    command_id
                )
            )
            conn.commit()
            return {"success": True}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "El nombre del comando ya existe"}

def delete_command(command_id):
    """DELETE: Elimina un comando desde la UI."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comandos WHERE id = ?", (command_id,))
        conn.commit()
        return {"success": True}

def toggle_command_status(command_id, status):
    """UPDATE: Cambia el estado (activo/inactivo) global."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE comandos SET active = ? WHERE id = ?", (status, command_id))
        conn.commit()
        return {"success": True}

# --- 5. LÓGICA DEL BOT (Para leer comandos en el chat) ---
# Esta función es la que usará tu bot de chat (no la UI)
def get_command_for_bot(command_name: str):
    """
    Obtiene los datos de un comando específico para que el bot lo ejecute.
    """
    with get_db_conn_dict() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comandos WHERE name = ?", (command_name.lower(),))
        row = cursor.fetchone()
        if row:
            return dict(row) # Devuelve el comando como un diccionario
        return None # No se encontró el comando


# --- INICIALIZACIÓN AUTOMÁTICA ---
# Se ejecuta la primera vez que alguien importa este archivo.
init_db()