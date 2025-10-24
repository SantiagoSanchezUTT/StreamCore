# Guarda esto en: streamcore/main.py
import webview
from api import Api # Importa la clase Api (que está en la misma carpeta)

# --- ¡CAMBIO AQUÍ! ---
# Usamos una RUTA RELATIVA simple.
# Pywebview es lo suficientemente inteligente para encontrarla
# e iniciar un servidor HTTP.
html_file = 'web/html/boceto_ui_config.html' 
# --- FIN DEL CAMBIO ---


if __name__ == '__main__':
    # 1. Crea una instancia de nuestra API
    api = Api()

    # 2. Crea la ventana y expone la API a JavaScript
    webview.create_window(
        'StreamCore - Configuración',
        html_file,      # <--- Pasa la ruta relativa
        js_api=api,
        width=800,
        height=600
    )
    
    # 3. Inicia la aplicación
    webview.start(debug=True)