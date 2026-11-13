"""
SHAIK-AI Voice Engine
Handles microphone input (STT) and speaker output (TTS).
Uses sounddevice instead of pyaudio — no C++ compiler required.
"""

import sys
import io
import wave
import threading
import pyttsx3
import speech_recognition as sr
from config import (
    TTS_RATE, TTS_VOLUME, TTS_VOICE,
    MIC_TIMEOUT, MIC_PHRASE_LIMIT, ENERGY_THRESHOLD
)

# Try sounddevice (preferred, no build needed)
try:
    import sounddevice as sd
    import numpy as np
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

# Fallback to pyaudio if somehow installed
try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False


# ── TTS Engine ─────────────────────────────────────────────────────────────────

class Speaker:
    def __init__(self):
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", TTS_RATE)
        self._engine.setProperty("volume", TTS_VOLUME)
        self._set_voice()
        self._lock = threading.Lock()

    def _set_voice(self):
        voices = self._engine.getProperty("voices")
        pref   = TTS_VOICE.lower()
        for v in voices:
            if pref in v.name.lower() or pref in (v.gender or "").lower():
                self._engine.setProperty("voice", v.id)
                return
        if voices:
            self._engine.setProperty("voice", voices[0].id)

    def say(self, text: str):
        print(f"[SHAIK-AI] {text}")
        with self._lock:
            self._engine.say(text)
            self._engine.runAndWait()


# ── SoundDevice Mic Source (replaces pyaudio) ──────────────────────────────────

class SoundDeviceMicSource:
    """
    A drop-in audio source for SpeechRecognition that uses sounddevice.
    No pyaudio / C++ compiler needed.
    """
    SAMPLE_RATE  = 16000
    SAMPLE_WIDTH = 2       # 16-bit = 2 bytes
    CHANNELS     = 1

    def __init__(self, device=None, sample_rate=16000):
        self.SAMPLE_RATE  = sample_rate
        self.device       = device
        self.stream       = None
        self._frames      = []

    def __enter__(self):
        self._frames = []
        self.stream  = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="int16",
            device=self.device,
            callback=self._callback,
        )
        self.stream.start()
        return self

    def _callback(self, indata, frames, time, status):
        self._frames.append(indata.copy())

    def __exit__(self, *args):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def read_audio(self, duration: float) -> sr.AudioData:
        """Record for `duration` seconds and return SpeechRecognition AudioData."""
        self._frames = []
        sd.sleep(int(duration * 1000))
        audio_np = np.concatenate(self._frames, axis=0) if self._frames else np.array([], dtype="int16")
        raw_data = audio_np.tobytes()
        return sr.AudioData(raw_data, self.SAMPLE_RATE, self.SAMPLE_WIDTH)


# ── STT Engine ─────────────────────────────────────────────────────────────────

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold       = ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self._mode = self._detect_mode()
        if self._mode == "sounddevice":
            print("[Voice] Using sounddevice backend ✓")
        elif self._mode == "pyaudio":
            print("[Voice] Using pyaudio backend ✓")
        else:
            print("[Voice] No mic backend found — keyboard mode active.")

    def _detect_mode(self) -> str:
        if HAS_SOUNDDEVICE:
            try:
                devices = sd.query_devices()
                inputs  = [d for d in devices if d["max_input_channels"] > 0]
                if inputs:
                    return "sounddevice"
            except Exception:
                pass
        if HAS_PYAUDIO:
            return "pyaudio"
        return "keyboard"

    # ── Sounddevice path ───────────────────────────────────────────────────
    def _listen_sounddevice(self) -> str | None:
        print("\n[Listening...] 🎤  (speak now)")
        try:
            recording = sd.rec(
                int(MIC_PHRASE_LIMIT * 16000),
                samplerate=16000,
                channels=1,
                dtype="int16"
            )
            sd.wait()   # wait until recording finishes

            # ── Write to IN-MEMORY buffer (no temp file = no file lock) ──
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(recording.tobytes())
            buf.seek(0)   # rewind to start

            with sr.AudioFile(buf) as source:
                audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio)
            print(f'[Heard] "{text}"')
            return text

        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[STT Error] {e}")
            return None
        except Exception as e:
            print(f"[Mic Error] {e}")
            return None

    # ── PyAudio path ───────────────────────────────────────────────────────
    def _listen_pyaudio(self) -> str | None:
        try:
            mic = sr.Microphone()
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("\n[Listening...] 🎤")
                audio = self.recognizer.listen(
                    source,
                    timeout=MIC_TIMEOUT,
                    phrase_time_limit=MIC_PHRASE_LIMIT
                )
            text = self.recognizer.recognize_google(audio)
            print(f'[Heard] "{text}"')
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[STT Error] {e}")
            return None

    # ── Public listen() ────────────────────────────────────────────────────
    def listen(self) -> str | None:
        if self._mode == "sounddevice":
            return self._listen_sounddevice()
        elif self._mode == "pyaudio":
            return self._listen_pyaudio()
        else:
            return self._keyboard_fallback()

    @staticmethod
    def _keyboard_fallback() -> str | None:
        try:
            text = input("⌨  Type command (or 'exit'): ").strip()
            return text if text else None
        except (EOFError, KeyboardInterrupt):
            return "exit"
