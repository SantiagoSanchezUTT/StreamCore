import json
import os
import pytest
import logging # <-- 1. Importa logging
from data import tokens as token_manager
from data.utils import get_persistent_data_path

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Captura todos los niveles
# Puedes añadir handlers si quieres guardar logs a archivo, etc.
# --- Fin Configuración Logger ---

REAL_CONFIG_PATH = get_persistent_data_path("kick_config.json")

def test_load_kick_config_reads_real_file():
    """Prueba que load_kick_config lee el archivo real existente."""
    logger.info("Inicio: test_load_kick_config_reads_real_file")
    expected_data = None
    if os.path.exists(REAL_CONFIG_PATH):
        logger.debug(f"Archivo real encontrado: {REAL_CONFIG_PATH}")
        try:
            with open(REAL_CONFIG_PATH, "r", encoding="utf-8") as f:
                expected_data = json.load(f)
            logger.debug(f"Datos esperados leídos: {expected_data}")
        except json.JSONDecodeError:
            logger.error(f"El archivo real {REAL_CONFIG_PATH} contiene JSON inválido.")
            pytest.fail("JSON inválido en archivo real.")
        except Exception as e:
            logger.error(f"No se pudo leer el archivo real {REAL_CONFIG_PATH}: {e}")
            pytest.fail("No se pudo leer archivo real.")
    else:
        logger.warning(f"Omitiendo prueba: El archivo real {REAL_CONFIG_PATH} no existe.")
        pytest.skip("Archivo real no existe.")

    logger.info("Act: Llamando a load_kick_config()")
    loaded_config = token_manager.load_kick_config()
    logger.debug(f"Resultado obtenido: {loaded_config}")

    logger.info("Assert: Verificando resultados...")
    assert loaded_config is not None, "load_kick_config devolvió None inesperadamente."
    assert loaded_config == expected_data
    logger.info("Fin: test_load_kick_config_reads_real_file - PASSED")

def test_load_kick_config_file_not_found_mocked(mocker):
    """Prueba que load_kick_config devuelve None si os.path.exists falla."""
    logger.info("Inicio: test_load_kick_config_file_not_found_mocked")
    logger.debug("Arrange: Mockeando os.path.exists para devolver False")
    mocker.patch('os.path.exists', return_value=False)

    logger.info("Act: Llamando a load_kick_config()")
    loaded_config = token_manager.load_kick_config()
    logger.debug(f"Resultado obtenido: {loaded_config}")

    logger.info("Assert: Verificando que el resultado es None...")
    assert loaded_config is None
    logger.info("Fin: test_load_kick_config_file_not_found_mocked - PASSED")

def test_load_kick_config_invalid_json_mocked(mocker):
    """Prueba que load_kick_config devuelve None si json.load falla."""
    logger.info("Inicio: test_load_kick_config_invalid_json_mocked")
    logger.debug("Arrange: Mockeando os.path.exists=True, json.load con error, y open()")
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('json.load', side_effect=json.JSONDecodeError("Simulated error", "doc", 0))
    mocker.patch('builtins.open', mocker.mock_open())

    logger.info("Act: Llamando a load_kick_config()")
    loaded_config = token_manager.load_kick_config()
    logger.debug(f"Resultado obtenido: {loaded_config}")

    logger.info("Assert: Verificando que el resultado es None...")
    assert loaded_config is None
    logger.info("Fin: test_load_kick_config_invalid_json_mocked - PASSED")