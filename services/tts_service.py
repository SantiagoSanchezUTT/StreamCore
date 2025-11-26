import threading
import queue
import os
import time
from gtts import gTTS
import pygame

class TTSService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.queue = queue.Queue()
        self.running = True
        self.volume = 0.8 # Volumen por defecto (0.0 a 1.0)
        
        pygame.mixer.init()

        # Suscripciones
        self.event_bus.subscribe("tts:speak", self._enqueue_message)
        self.event_bus.subscribe("tts:config", self._update_config) # <--- NUEVO
        
        self.thread = threading.Thread(target=self._worker_loop, daemon=True, name="TTS_Worker")
        self.thread.start()
        print("(TTS Service gTTS) Motor backend iniciado.")

    def _update_config(self, settings):
        """Actualiza el volumen en tiempo real"""
        if 'volume' in settings:
            self.volume = float(settings['volume'])
            # pygame maneja volumen de 0.0 a 1.0
            try:
                pygame.mixer.music.set_volume(self.volume)
                print(f"[TTS Config] Volumen ajustado a {self.volume}")
            except Exception:
                pass

    def _enqueue_message(self, data):
        text = data.get("message", "") if isinstance(data, dict) else str(data)
        if text:
            self.queue.put(text)

    def _worker_loop(self):
        while self.running:
            try:
                text = self.queue.get(timeout=1)
                
                filename = f"temp_tts_{int(time.time())}.mp3"
                tts = gTTS(text=text, lang='es')
                tts.save(filename)
                
                pygame.mixer.music.load(filename)
                pygame.mixer.music.set_volume(self.volume) # <--- APLICAR VOLUMEN ANTES DE PLAY
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                os.remove(filename)
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS Error] {e}")