# Pruebas de StreamCore

Instrucciones para ejecutar la suite de pruebas y generar reportes locales.

Requisitos
- Python 3.10+ instalado
- (Opcional) crear y activar un entorno virtual: `python -m venv .venv && source .venv/bin/activate`
- Instalar dependencias: `pip install -r requirements.txt`
- Instalar herramientas de test si no están en requirements: `pip install pytest pytest-cov`

Ejecución local rápida
- Ejecutar todos los tests y generar reportes:
  - `bash scripts/run_tests.sh`

- Ejecutar solo tests unitarios (si usas marcas para separar):
  - `pytest -m "not integration"`

- Ejecutar solo tests de integración:
  - `pytest -m integration`

Resultados y artefactos
- JUnit XML: tests/results/junit.xml
- Coverage XML: tests/results/coverage.xml
- Coverage HTML: tests/results/htmlcov/index.html

Ver cobertura HTML localmente:
- Abre `tests/results/htmlcov/index.html` en tu navegador.

CI (GitHub Actions)
- Hay un workflow `ci.yml` que ejecuta tests para Python 3.10 y 3.11, sube los artefactos (JUnit + cobertura).
- Hay un workflow `integration.yml` invocable manualmente para ejecutar tests marcados como `integration`.

Buenas prácticas
- No incluyas credenciales reales en tests. Usa variables de entorno y mocks para integrar con Twitch/Kick.
- Marca tests que dependen de servicios externos con `@pytest.mark.integration`.
- Mantén tests unitarios rápidos y deterministas. Evita sleeps largos: usa sincronización/fixtures.

Si quieres, puedo:
- Crear un ejemplo de Docker Compose para levantar fakes (Twitch/Kick).
- Preparar un job adicional que envíe cobertura a Codecov / Coveralls.