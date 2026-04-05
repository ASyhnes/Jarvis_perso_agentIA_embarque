import sounddevice as sd
import numpy as np
import wave
import subprocess
import time
import sys
import os

def record_audio(duration, filename="test_mic.wav"):
    print(f"🎤 Enregistrement de {duration} secondes en cours...")
    try:
        device_info = sd.query_devices(kind='input')
        samplerate = int(device_info['default_samplerate'])
    except Exception as e:
        print(f"⚠️ Erreur de détection de la fréquence d'échantillonnage : {e}. Utilisation de 16000Hz (standard Whisper).")
        samplerate = 16000 

    try:
        # Standard whisper sample rate is 16kHz
        # It's better to record at 16kHz directly if supported or resample. SD can resample.
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        
        # Draw a little progress bar
        for i in range(int(duration)):
            time.sleep(1)
            print(f"... {i+1}s")
            
        sd.wait()
        print("✅ Enregistrement terminé.")
        
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())
            
        return filename
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement : {e}")
        return None

def transcribe_audio(filename):
    print("\n📝 Transcription avec Whisper...")
    start_time = time.time()
    
    # Check if a model exists
    model_path = "./whisper.cpp/models/ggml-base.bin"
    if not os.path.exists(model_path):
        print(f"⚠️  Attention: le modèle Whisper {model_path} est introuvable.")
        print("Il se peut que la transcription échoue.")
    
    try:
        # On va d'abord lister le contenu du dossier whisper au cas où nous devons déboguer
        result = subprocess.run(
            ["./whisper.cpp/build/bin/whisper-cli", "-m", model_path, "-l", "fr", "-t", "4", "-f", filename, "-nt"],
            capture_output=True, text=True
        )
        print(f"\n--- Sortie de Whisper ---")
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("(Aucune sortie / Silence)")
            
        if result.stderr and "error" in result.stderr.lower():
            print("\n--- Erreurs (stderr) ---")
            print(result.stderr)
            
        print(f"\n⏳ Temps de transcription : {time.time() - start_time:.2f} secondes")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de Whisper : {e}")
        print("Avez-vous compilé whisper.cpp ?")
        
if __name__ == "__main__":
    duration = 5
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            pass
            
    audio_file = record_audio(duration)
    if audio_file:
        transcribe_audio(audio_file)
