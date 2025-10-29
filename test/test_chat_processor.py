import pytest
import logging # <-- Importa logging
from processing import chat_processor

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# --- Fin Configuración Logger ---

@pytest.fixture(autouse=True)
def mock_event_bus(mocker):
    logger.debug("Fixture: mock_event_bus - Aplicando mock a processing.chat_processor.bus")
    mock_bus = mocker.patch('processing.chat_processor.bus')
    return mock_bus

def test_process_ping_command(mock_event_bus):
    """Verifica que !ping publica command:reply con '¡pong!'."""
    logger.info("Inicio: test_process_ping_command")
    test_data = {"platform": "kick", "sender": "User1", "content": "!ping", "raw_message": {}}
    logger.debug(f"Arrange: Datos de prueba = {test_data}")

    logger.info("Act: Llamando a process_chat_message()")
    chat_processor.process_chat_message(test_data)

    logger.info("Assert: Verificando llamada a bus.publish...")
    expected_payload = {"platform": "kick", "response": "¡pong!", "original_message": test_data}
    mock_event_bus.publish.assert_called_once_with("command:reply", expected_payload)
    logger.info("Fin: test_process_ping_command - PASSED")

def test_process_hola_command(mock_event_bus):
    """Verifica que !hola publica command:reply con el saludo."""
    logger.info("Inicio: test_process_hola_command")
    test_data = {"platform": "kick", "sender": "User2", "content": "!hola "}
    logger.debug(f"Arrange: Datos de prueba = {test_data}")

    logger.info("Act: Llamando a process_chat_message()")
    chat_processor.process_chat_message(test_data)

    logger.info("Assert: Verificando llamada a bus.publish...")
    expected_payload = {"platform": "kick", "response": "¡Hola User2! 👋", "original_message": test_data}
    mock_event_bus.publish.assert_called_once_with("command:reply", expected_payload)
    logger.info("Fin: test_process_hola_command - PASSED")

def test_process_non_command(mock_event_bus):
    """Verifica que un mensaje normal no publica command:reply."""
    logger.info("Inicio: test_process_non_command")
    test_data = {"platform": "kick", "sender": "User3", "content": "Hola como estas"}
    logger.debug(f"Arrange: Datos de prueba = {test_data}")

    logger.info("Act: Llamando a process_chat_message()")
    chat_processor.process_chat_message(test_data)

    logger.info("Assert: Verificando que bus.publish NO fue llamado para command:reply...")
    calls = mock_event_bus.publish.call_args_list
    command_reply_called = any(call.args[0] == "command:reply" for call in calls)
    assert not command_reply_called
    logger.info("Fin: test_process_non_command - PASSED")