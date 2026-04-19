import sounddevice as sd
import numpy as np

print("Available audio devices:")
print(sd.query_devices())

print("\n" + "="*50)
print("Testing default input...")

try:
    # Test 3-second recording
    print("Recording 3 seconds... SPEAK NOW")
    audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype=np.int16)
    sd.wait()
    print(f"✓ Captured {len(audio)} samples")
    print(f"Audio range: {audio.min()} to {audio.max()}")
    
    if audio.max() > 100:
        print("✓ Sound detected!")
    else:
        print("✗ No sound detected - check microphone permissions")
        
except Exception as e:
    print(f"✗ Error: {e}")