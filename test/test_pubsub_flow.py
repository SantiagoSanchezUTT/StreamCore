import pytest
import asyncio
import logging # <-- Importa logging
from event_bus import bus
from connectors import kick_connector
from processing import chat_processor, sender_processor

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# --- Fin Configuración Logger ---

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def ensure_subscriptions(mocker):
    logger.debug("Fixture: ensure_subscriptions - Mockeando sender_processor.send_kick_message")
    mock_send = mocker.patch('processing.sender_processor.send_kick_message')
    # Podrías necesitar re-importar o suscribir explícitamente si limpias el bus
    # bus.subscribe("chat:message_received", chat_processor.process_chat_message)
    # bus.subscribe("command:reply", sender_processor.handle_reply_event)
    return mock_send

async def test_ping_flow_integration(ensure_subscriptions):
    """Prueba el flujo completo desde el mensaje hasta el intento de envío."""
    logger.info("Inicio: test_ping_flow_integration")
    kick_message_data = {'sender_username': 'Tester', 'content': ' !ping ', 'badges': [], 'created_at': '...', 'chat_id': '12345'}
    logger.debug(f"Arrange: Datos de mensaje Kick simulado = {kick_message_data}")

    connector_instance = kick_connector.KickConnector()
    logger.info("Act: Llamando a _handle_message del conector...")
    await connector_instance._handle_message(kick_message_data)

    logger.debug("Act: Esperando procesamiento del bus...")
    await asyncio.sleep(0.1) # Pausa para asyncio

    logger.info("Assert: Verificando que send_kick_message fue llamado con '¡pong!'...")
    ensure_subscriptions.assert_called_once_with("¡pong!")
    logger.info("Fin: test_ping_flow_integration - PASSED")