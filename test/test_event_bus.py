import time
import pytest

# Ajusta la importación según la implementación real
try:
    from event_bus import EventBus
except Exception:
    EventBus = None

@pytest.mark.skipif(EventBus is None, reason="No EventBus disponible")
def test_publish_subscribe_simple():
    bus = EventBus()
    received = []

    def handler(evt):
        received.append(evt)

    bus.subscribe('my_event', handler)
    bus.publish('my_event', {'x': 1})
    # Si publish es asíncrono, esperar un corto tiempo
    time.sleep(0.05)
    assert len(received) == 1
    assert received[0]['x'] == 1

@pytest.mark.skipif(EventBus is None, reason="No EventBus disponible")
def test_handler_exception_does_not_block_others():
    bus = EventBus()
    received = []

    def bad_handler(evt):
        raise RuntimeError("boom")

    def good_handler(evt):
        received.append(evt)

    bus.subscribe('e', bad_handler)
    bus.subscribe('e', good_handler)
    bus.publish('e', {'ok': True})
    time.sleep(0.05)
    assert len(received) == 1