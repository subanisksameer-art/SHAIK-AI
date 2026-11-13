"""Quick mic test - no temp files, pure in-memory recording"""
import io
import wave
import sounddevice as sd
import speech_recognition as sr

RATE     = 16000
SECONDS  = 5

print("Recording for 5 seconds... SPEAK NOW!")
recording = sd.rec(int(SECONDS * RATE), samplerate=RATE, channels=1, dtype="int16")
sd.wait()
print("Done recording. Processing...")

# In-memory buffer — no temp file, no WinError 32
buf = io.BytesIO()
with wave.open(buf, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(recording.tobytes())
buf.seek(0)

recognizer = sr.Recognizer()
with sr.AudioFile(buf) as source:
    audio = recognizer.record(source)

try:
    text = recognizer.recognize_google(audio)
    print(f'\n✅ You said: "{text}"')
except sr.UnknownValueError:
    print("\n❌ Could not understand. Speak louder/clearer.")
except sr.RequestError as e:
    print(f"\n❌ Internet error: {e}")
