import os
import sqlite3
from datetime import datetime
import time

# --- Ruta a la base de datos ---
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/usage_kick.db")

# --- Función para conexión ---
def get_connection():
    return sqlite3.connect(DB_PATH)

# --- Función para inicializar base de datos si no existe ---
def ensure_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plataforma TEXT NOT NULL,
            nickname TEXT NOT NULL,
            total_asistencias INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comandos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comando TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            nivel TEXT DEFAULT 'normal',
            tiempo_refresco INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


# --- MENÚ PRINCIPAL ---
def main_menu():
    ensure_database()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("🧩 PANEL DE GESTIÓN KICK BOT\n")
        print("1️⃣  Ver usuarios más activos")
        print("2️⃣  Ver asistencias")
        print("3️⃣  Definir o editar comandos")
        print("4️⃣  Salir\n")

        option = input("Selecciona una opción: ").strip()

        if option == "1":
            view_active_users()
        elif option == "2":
            manage_asistencias()
        elif option == "3":
            manage_comandos()
        elif option == "4":
            print("👋 Cerrando panel...")
            time.sleep(1)
            break
        else:
            print("❌ Opción no válida.")
            time.sleep(1)


# --- 1️⃣ Ver usuarios más activos ---
def view_active_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, COUNT(*) as total_msgs
        FROM chat_usage
        GROUP BY username
        ORDER BY total_msgs DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    print("\n🏆 Usuarios más activos:\n")
    if not rows:
        print("No hay datos de chat registrados aún.\n")
    else:
        for i, (user, total) in enumerate(rows, 1):
            print(f"{i}. {user:<20} {total} mensajes")
    input("\nPresiona Enter para volver al menú...")


# --- 2️⃣ Gestión de asistencias ---
def manage_asistencias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, plataforma, nickname, total_asistencias FROM asistencias ORDER BY total_asistencias DESC")
    rows = cursor.fetchall()
    conn.close()

    print("\n📋 Asistencias registradas:\n")
    if not rows:
        print("No hay asistencias registradas.")
    else:
        for r in rows:
            print(f"ID {r[0]} | {r[1]} | {r[2]} → {r[3]} asistencias")

    print("\nOpciones:")
    print("1️⃣  Añadir asistencia")
    print("2️⃣  Regresar")

    opt = input("\nSelecciona una opción: ").strip()
    if opt == "1":
        add_asistencia()
    else:
        return


def add_asistencia():
    plataforma = input("Plataforma (ej. Kick): ").strip()
    nickname = input("Nickname del usuario: ").strip()
    if not nickname:
        print("❌ Nickname no puede estar vacío.")
        time.sleep(1)
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total_asistencias FROM asistencias WHERE nickname=? AND plataforma=?", (nickname, plataforma))
    row = cursor.fetchone()

    if row:
        total = row[0] + 1
        cursor.execute("UPDATE asistencias SET total_asistencias=? WHERE nickname=? AND plataforma=?", (total, nickname, plataforma))
    else:
        cursor.execute("INSERT INTO asistencias (plataforma, nickname, total_asistencias) VALUES (?, ?, 1)", (plataforma, nickname))

    conn.commit()
    conn.close()
    print(f"✅ Asistencia registrada para {nickname}.")
    time.sleep(1)


# --- 3️⃣ Gestión de comandos ---
def manage_comandos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, comando, respuesta, nivel, tiempo_refresco FROM comandos")
    rows = cursor.fetchall()
    conn.close()

    print("\n⚙️  Comandos actuales:\n")
    if not rows:
        print("No hay comandos definidos.")
    else:
        for r in rows:
            print(f"ID {r[0]} | !{r[1]} → {r[2]} | Nivel: {r[3]} | Cooldown: {r[4]}s")

    print("\nOpciones:")
    print("1.- Agregar comando")
    print("2.- Editar comando")
    print("3.- Eliminar comando")
    print("4.- Regresar")

    opt = input("\nSelecciona una opción: ").strip()
    if opt == "1":
        add_comando()
    elif opt == "2":
        edit_comando()
    elif opt == "3":
        delete_comando()
    else:
        return


def add_comando():
    comando = input("Nombre del comando (sin '!'): ").strip()
    respuesta = input("Respuesta del comando: ").strip()
    nivel = input("Nivel (normal/suscriptor): ").strip() or "normal"
    try:
        cooldown = int(input("Tiempo de refresco (segundos): ").strip() or 0)
    except:
        cooldown = 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comandos (comando, respuesta, nivel, tiempo_refresco) VALUES (?, ?, ?, ?)",
                   (comando, respuesta, nivel, cooldown))
    conn.commit()
    conn.close()
    print(f"✅ Comando '!{comando}' agregado.")
    time.sleep(1)


def edit_comando():
    cmd_id = input("ID del comando a editar: ").strip()
    if not cmd_id.isdigit():
        print("❌ ID inválido.")
        time.sleep(1)
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT comando, respuesta, nivel, tiempo_refresco FROM comandos WHERE id=?", (cmd_id,))
    row = cursor.fetchone()
    if not row:
        print("❌ Comando no encontrado.")
        conn.close()
        time.sleep(1)
        return

    comando, respuesta, nivel, tiempo_refresco = row
    print(f"\nEditando '!{comando}' (Enter para dejar igual):")
    new_resp = input(f"Nueva respuesta [{respuesta}]: ").strip() or respuesta
    new_nivel = input(f"Nuevo nivel [{nivel}]: ").strip() or nivel
    try:
        new_cool = int(input(f"Nuevo tiempo de refresco [{tiempo_refresco}]: ").strip() or tiempo_refresco)
    except:
        new_cool = tiempo_refresco

    cursor.execute("UPDATE comandos SET respuesta=?, nivel=?, tiempo_refresco=? WHERE id=?",
                   (new_resp, new_nivel, new_cool, cmd_id))
    conn.commit()
    conn.close()
    print("✅ Comando actualizado.")
    time.sleep(1)


def delete_comando():
    cmd_id = input("ID del comando a eliminar: ").strip()
    if not cmd_id.isdigit():
        print("❌ ID inválido.")
        time.sleep(1)
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comandos WHERE id=?", (cmd_id,))
    conn.commit()
    conn.close()
    print("🗑️  Comando eliminado.")
    time.sleep(1)


# --- EJECUCIÓN DIRECTA ---
if __name__ == "__main__":
    main_menu()