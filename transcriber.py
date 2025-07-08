import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()
model = Model("model/vosk-model-en-us-0.22")  # Path to your Vosk model folder
rec = KaldiRecognizer(model, 16000)

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

def record_and_transcribe(duration=10):
    text = ""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        for _ in range(0, int(16000 / 8000 * duration)):
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get("text", "") + " "
        final_result = json.loads(rec.FinalResult())
        text += final_result.get("text", "")
    return text.strip()
