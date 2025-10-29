import pytest
import responses
import json
import logging # <-- Importa logging
from processing import sender_processor

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# --- Fin Configuración Logger ---

pytestmark = pytest.mark.asyncio

KICK_CHAT_URL = "https://api.kick.com/public/v1/chat"

@pytest.fixture
def mock_kick_dependencies(mocker):
    """Mockea las dependencias de token y config."""
    logger.debug("Fixture: mock_kick_dependencies - Aplicando mocks a data.tokens")
    mocker.patch('data.tokens.get_kick_token_from_db', return_value="fake_access_token")
    mocker.patch('data.tokens.load_kick_config', return_value={"BROADCASTER_ID": 98765})

@responses.activate
async def test_send_kick_message_success(mock_kick_dependencies):
    """Prueba el envío exitoso a la API de Kick."""
    logger.info("Inicio: test_send_kick_message_success")
    logger.debug(f"Arrange: Configurando mock de responses para POST {KICK_CHAT_URL} -> 200 OK")
    responses.add(method=responses.POST, url=KICK_CHAT_URL,
                  json={"data": {"message_id": "fake_id", "is_sent": True}, "message": "OK"}, status=200)
    test_message = "Mensaje de prueba"
    logger.debug(f"Arrange: Mensaje a enviar = '{test_message}'")

    logger.info("Act: Llamando a send_kick_message()")
    await sender_processor.send_kick_message(test_message)

    logger.info("Assert: Verificando llamada a API...")
    assert len(responses.calls) == 1
    call = responses.calls[0]
    # (Asserts de la llamada como los tenías)
    assert call.request.url == KICK_CHAT_URL
    sent_payload = json.loads(call.request.body)
    assert sent_payload['content'] == test_message
    logger.debug("Assert: Llamada a API verificada.")
    logger.info("Fin: test_send_kick_message_success - PASSED")

@responses.activate
async def test_send_kick_message_unauthorized(mock_kick_dependencies, capsys):
    """Prueba el manejo de un error 401 Unauthorized."""
    logger.info("Inicio: test_send_kick_message_unauthorized")
    logger.debug(f"Arrange: Configurando mock de responses para POST {KICK_CHAT_URL} -> 401 Unauthorized")
    responses.add(method=responses.POST, url=KICK_CHAT_URL,
                  json={"message": "Unauthorized"}, status=401)
    test_message = "Otro mensaje"
    logger.debug(f"Arrange: Mensaje a enviar = '{test_message}'")

    logger.info("Act: Llamando a send_kick_message()")
    await sender_processor.send_kick_message(test_message)

    logger.info("Assert: Verificando salida de error en consola...")
    captured = capsys.readouterr()
    assert "Error 401" in captured.out
    assert "Unauthorized" in captured.out
    logger.debug(f"Assert: Salida capturada = {captured.out.strip()}")
    logger.info("Fin: test_send_kick_message_unauthorized - PASSED")