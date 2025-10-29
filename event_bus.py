import asyncio
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        print("Event Bus inicializado.")

    def subscribe(self, event_type: str, callback):
        """Registra una función para escuchar un evento."""
        print(f"Suscribiendo '{getattr(callback, '__name__', 'callback')}' al evento '{event_type}'")
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        """Elimina una suscripción."""
        try:
            self._subscribers[event_type].remove(callback)
            print(f"Desuscribiendo '{getattr(callback, '__name__', 'callback')}' del evento '{event_type}'")
        except ValueError:
            pass # Ignora si no estaba suscrito

    def publish(self, event_type: str, data=None):
        """Envía un evento a todos los suscriptores."""
        print(f"Publicando evento '{event_type}' con datos: {data}")
        if event_type in self._subscribers:
            # Usamos asyncio.create_task para no bloquear si un callback es async
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(data))
                else:
                    try:
                        # Si el callback no es async, lo ejecutamos directamente
                        # Idealmente, callbacks largos deberían ser async o correr en hilos
                        callback(data)
                    except Exception as e:
                        print(f"Error ejecutando callback síncrono para '{event_type}': {e}")


# Instancia global única del bus de eventos
# Otros módulos importarán esta instancia: from event_bus import bus
bus = EventBus()