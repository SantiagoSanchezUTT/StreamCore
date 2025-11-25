import http.server
import socketserver
import threading
import os

def start_static_server(directory, port=8001):
    """
    Servidor HTTP miniatura que expone SOLO los archivos MP3 del TTS.
    Usado para evitar problemas de PyWebview con file:///
    """
    os.makedirs(directory, exist_ok=True)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            # Solo sirve los MP3 desde la carpeta destino
            filename = os.path.basename(path)
            return os.path.join(directory, filename)

        def log_message(self, format, *args):
            return  # Silencia logging feo

    httpd = socketserver.TCPServer(("", port), Handler)
    print(f"[TTS-Server] Servidor estático iniciado en http://localhost:{port}/")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
