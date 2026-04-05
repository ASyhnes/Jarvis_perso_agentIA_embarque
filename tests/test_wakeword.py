import sounddevice as sd
import numpy as np
import scipy.signal
import openwakeword
from openwakeword.model import Model
import time

WAKE_WORD_MODEL = "./wakeword.onnx"
WAKE_WORD_THRESHOLD = 0.2
CHUNK_SIZE = 1280
OWW_SAMPLE_RATE = 16000

print(f"Chargement du modèle OpenWakeWord : {WAKE_WORD_MODEL}")
# Try to load the model (copying the same logic from agent.py)
oww_model = None
try:
    oww_model = Model(wakeword_model_paths=[WAKE_WORD_MODEL])
except TypeError:
    try:
        oww_model = Model(wakeword_models=[WAKE_WORD_MODEL])
    except Exception as e:
        print(f"Erreur de chargement du modèle: {e}")
except Exception as e:
    print(f"Erreur de chargement du modèle: {e}")

if not oww_model:
    print("❌ Impossible de charger le modèle de mot de réveil.")
    exit(1)

print("✅ Modèle chargé avec succès !")

try:
    device_info = sd.query_devices(kind='input')
    native_rate = int(device_info['default_samplerate'])
except Exception as e:
    print(f"⚠️ Erreur de détection de la fréquence d'échantillonnage: {e}")
    native_rate = 44100

use_resampling = (native_rate != OWW_SAMPLE_RATE)
input_rate = native_rate if use_resampling else OWW_SAMPLE_RATE
input_chunk_size = int(CHUNK_SIZE * (input_rate / OWW_SAMPLE_RATE)) if use_resampling else CHUNK_SIZE

print(f"🎤 Écoute en cours (Fréquence: {input_rate}Hz → {OWW_SAMPLE_RATE}Hz)... Dites 'Hey Jarvis' !")
print("Afficheur de probabilité (0.0 à 1.0) :")
print("-" * 50)

try:
    with sd.InputStream(samplerate=input_rate, channels=1, dtype='int16', blocksize=input_chunk_size) as stream:
        while True:
            data, overflowed = stream.read(input_chunk_size)
            if overflowed:
                pass
                
            # Convert raw bytes to numpy array of int16
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Boost the volume
            # We multiply in float first to prevent integer overflow wrapping
            float_data = audio_data.astype(np.float32)
            float_data = float_data * 5.0
            np.clip(float_data, -32768, 32767, out=float_data)
            audio_data = float_data.astype(np.int16)

            if use_resampling:
                 audio_data = scipy.signal.resample(audio_data, CHUNK_SIZE).astype(np.int16)

            prediction = oww_model.predict(audio_data)
            
            model_names = list(oww_model.prediction_buffer.keys())
            if not model_names:
                continue
            model_name = model_names[0]
            
            score = list(oww_model.prediction_buffer[model_name])[-1]
            
            bar_length = int(score * 40)
            bar = "█" * bar_length
            
            if score > WAKE_WORD_THRESHOLD:
                print(f"\r[ {score:.3f} ] {bar:<40} 🚨 RÉVEIL DÉTECTÉ !! 🚨", end="", flush=True)
                oww_model.reset()
                time.sleep(1) 
            else:
                # Debug volume visualization: show if we're actually hearing *anything*
                vol = np.abs(audio_data).mean()
                vol_bar = "=" * int(min(vol / 100, 10))
                print(f"\r[ {score:.3f} ] {bar:<40} | Vol: {vol_bar:<10}", end="", flush=True)
                
except KeyboardInterrupt:
    print("\n\nTest arrêté.")
except Exception as e:
    print(f"\n❌ Erreur pendant le stream audio: {e}")
