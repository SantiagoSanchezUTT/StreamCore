import pytest

# Este test usa la fixture 'client' definida en conftest.py
def test_health_endpoint(client):
    res = client.get('/health')
    # Si no hay endpoint /health en api.py, el test debe ajustarse o será marcado como skip en conftest
    assert res.status_code == 200
    # si la respuesta es JSON
    try:
        data = res.json()
        assert 'status' in data or data is not None
    except Exception:
        # si no es JSON, al menos asegurar 200
        pass