import importlib
import pytest

# Intentamos detectar una aplicación expuesta en api.py como 'app'
app = None
try:
    api_mod = importlib.import_module('api')
    app = getattr(api_mod, 'app', None)
except Exception:
    app = None

@pytest.fixture
def client():
    """
    Devuelve un cliente de pruebas para Flask o FastAPI/Starlette si se detecta.
    Si no hay 'app' en api.py se hace skip de los tests que lo requieran.
    """
    if app is None:
        pytest.skip("No se encontró 'app' en api.py (fixture client)")

    # Flask-compatible app
    if hasattr(app, 'test_client'):
        with app.test_client() as c:
            yield c
        return

    # FastAPI / Starlette app
    try:
        from starlette.testclient import TestClient
        yield TestClient(app)
        return
    except Exception:
        pass

    pytest.skip("No se pudo crear test client para la app detectada")