import pyttsx3
import random
import time
from processing.tts_config import CONFIG

class OfflineTTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.startLoop(False)

        self.voices = self.engine.getProperty("voices")

        self.male_voices = [v for v in self.voices if "male" in v.id.lower()]
        self.female_voices = [v for v in self.voices if "female" in v.id.lower()]

        self.speed = CONFIG["speed"]
        self.volume = CONFIG["volume"]
        self.pitch = CONFIG["pitch"]
        self.random_mode = CONFIG["voice_mode"]
        self.selected_voice = None

        if CONFIG["voice_mode"] == "single" and CONFIG["voice_index"] is not None:
            self.selected_voice = self.voices[CONFIG["voice_index"]]

        self.engine.setProperty("rate", self.speed)
        self.engine.setProperty("volume", self.volume)

    # ==========================================
    def apply_voice(self):
        if self.random_mode == "single" and self.selected_voice:
            self.engine.setProperty("voice", self.selected_voice.id)

        elif self.random_mode == "male":
            v = random.choice(self.male_voices)
            self.engine.setProperty("voice", v.id)

        elif self.random_mode == "female":
            v = random.choice(self.female_voices)
            self.engine.setProperty("voice", v.id)

        elif self.random_mode == "any":
            v = random.choice(self.voices)
            self.engine.setProperty("voice", v.id)

    # ==========================================
    def speak(self, text):

        # Evita bug de bloqueos
        self.engine.stop()

        self.apply_voice()

        rate = self.speed
        if self.pitch < 80:
            rate -= 20
        elif self.pitch > 80:
            rate += 20

        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", self.volume)

        self.engine.say(text)
        self.engine.iterate()

        time.sleep(0.05)
