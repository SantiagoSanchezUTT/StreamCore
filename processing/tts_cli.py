import sys
import subprocess
import tempfile
import os

# Texto a convertir
text = sys.argv[1]

# Posibles rutas de Edge
possible_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Users\{}\\AppData\Local\Microsoft\Edge\Application\msedge.exe".format(os.getenv("USERNAME")),
]

edge_path = None

for p in possible_paths:
    if os.path.exists(p):
        edge_path = p
        break

if edge_path is None:
    print("ERROR: No se encontró msedge.exe")
    sys.exit(1)

# Archivo temporal de salida
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
output_path = tmp.name
tmp.close()

# Comando
command = [
    edge_path,
    "--headless",
    f'--speak="{text}"',
    f'--output-file="{output_path}"'
]

try:
    subprocess.run(command, check=True)
    print(output_path)
except Exception as e:
    print(f"ERROR:{e}")
    sys.exit(1)
