import whisper
import numpy as np
import tempfile
import wave
import os
import warnings

# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception as e:
    print(f"Sounddevice not available: {e}")
    SOUNDDEVICE_AVAILABLE = False

class AudioRecorder:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model ({model_size})... This takes 10-30 seconds first time.")
        self.model = whisper.load_model(model_size)
        self.sample_rate = 16000
        print("✓ Model ready")
    
    def record(self, duration=60):
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("Microphone not available. Use file upload instead.")
        
        print(f"🔴 Recording for {duration} seconds... SPEAK NOW")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocking=True
        )
        print("✓ Recording complete")
        return audio
    
    def save_wav(self, audio, filepath=None):
        if filepath is None:
            filepath = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())
        return filepath
    
    def transcribe(self, audio_path):
        result = self.model.transcribe(
            audio_path, 
            word_timestamps=True,
            fp16=False  # Force FP32 for Windows CPU compatibility
        )
        
        # Extract words with timing
        words = []
        for seg in result.get("segments", []):
            for word in seg.get("words", []):
                words.append({
                    "word": word["word"],
                    "start": word["start"],
                    "end": word["end"]
                })
        
        return {
            "full_text": result["text"].strip(),
            "words": words,
            "language": result.get("language", "en"),
            "duration": result.get("duration", 0)
        }
    
    def record_and_transcribe(self, duration=60):
        """One-shot record + transcribe with cleanup"""
        audio = self.record(duration)
        temp_path = self.save_wav(audio)
        try:
            result = self.transcribe(temp_path)
            return result
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)