import sqlite3
from .utils import get_persistent_data_path 

# --- 1. RUTA ÚNICA Y CENTRALIZADA ---
DB_PATH = get_persistent_data_path("bot_database.db")
print(f"Base de datos unificada en: {DB_PATH}")

# --- 2. CONEXIÓN ÚNICA ---
def get_connection():
    return sqlite3.connect(DB_PATH)

# --- 3. INICIALIZACIÓN (Lógica de !asistencia) ---
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabla 1: Asistencias (Tu lógica de lealtad)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                nickname TEXT NOT NULL,
                total_asistencias INTEGER DEFAULT 1,
                UNIQUE(nickname, platform)
            )
        """)

        # Tabla 2: Comandos (Para !redes, !hola, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                response TEXT NOT NULL,
                platform TEXT NOT NULL,
                level TEXT DEFAULT 'normal',
                refresh_time INTEGER DEFAULT 0,
                UNIQUE(command, platform)
            )
        """)
        
        conn.commit()
    print("🧩 Tablas de Base de Datos (Asistencias y Comandos) aseguradas.")


# --- 4. FUNCIONES CRUD ---

# --- Funciones de Asistencia ---
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
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, platform, nickname, total_asistencias 
            FROM asistencias ORDER BY total_asistencias DESC
        """)
        return cursor.fetchall()

# --- Funciones de Comandos ---
def add_command(command: str, response: str, platform: str, level: str = 'normal', refresh_time: int = 0):
    """
    Añade o REEMPLAZA un comando para una plataforma.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO commands (command, response, platform, level, refresh_time)
            VALUES (?, ?, ?, ?, ?)
        """, (command.lower(), response, platform.lower(), level, refresh_time))
        conn.commit()

def get_command(command: str, platform: str):
    """Obtiene un comando específico para una plataforma."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT response, level, refresh_time FROM commands WHERE command = ? AND platform = ?", 
                       (command.lower(), platform.lower()))
        return cursor.fetchone()

def list_commands(platform: str = None):
    """Lista todos los comandos, opcionalmente filtrados por plataforma."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if platform:
            cursor.execute("SELECT * FROM commands WHERE platform = ?", (platform.lower(),))
        else:
            cursor.execute("SELECT * FROM commands ORDER BY platform, command")
        return cursor.fetchall()

def delete_command(command_id: int):
    """Elimina un comando por su ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM commands WHERE id = ?", (command_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_command(command_id: int, response: str, level: str, refresh_time: int):
    """Actualiza un comando por su ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE commands SET response = ?, level = ?, refresh_time = ?
            WHERE id = ?
        """, (response, level, refresh_time, command_id))
        conn.commit()
        return cursor.rowcount > 0

# --- INICIALIZACIÓN AUTOMÁTICA ---
# Se ejecuta la primera vez que alguien importa este archivo.
init_db()