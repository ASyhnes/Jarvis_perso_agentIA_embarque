import sounddevice as sd
import numpy as np
import wave
import subprocess
import time
import re

INPUT_DEVICE_NAME = None

def get_input_device():
    global INPUT_DEVICE_NAME
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ('USB' in dev['name'] or 'Audio' in dev['name']):
            INPUT_DEVICE_NAME = dev['name']
            return dev['name']
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ('sysdefault' in dev['name'] or 'default' in dev['name']):
            INPUT_DEVICE_NAME = dev['name']
            return dev['name']
    return None

def record_and_transcribe():
    device = get_input_device()
    if not device:
        print("❌ Aucun micro trouvé.")
        return
        
    print(f"🎤 Micro sélectionné : {device}")
    
    samplerate = 44100
    chunk_duration = 0.05
    chunk_size = int(samplerate * chunk_duration)
    
    speech_threshold = 1500   # Volume nécessaire pour éveiller l'agent
    silence_threshold = 1000  # Niveau auquel on considère que la personne a arrêté de parler
    silence_duration = 1.5
    
    buffer = []
    recorded_chunks = 0
    silent_chunks = 0
    speaking_started = False
    
    print("\n" + "="*50)
    print("PARLEZ MAINTENANT (Je m'arrêterai quand vous ferez silence...)")
    print("="*50)

    def callback(indata, frames, time_info, status):
        nonlocal silent_chunks, recorded_chunks, speaking_started
        
        float_data = indata.astype(np.float32) * 5.0
        np.clip(float_data, -32768, 32767, out=float_data)
        boosted = float_data.astype(np.int16)
        
        buffer.append(boosted.copy())
        recorded_chunks += 1
        
        # Lissage avec moyenne glissante
        volume = np.sqrt(np.mean(boosted.astype(np.float32)**2))
        
        # Hystérésis de déclenchement
        if not speaking_started and volume > speech_threshold:
            speaking_started = True
            silent_chunks = 0
            
        if speaking_started:
            if volume < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0 # Remise à zéro si on reparle au-dessus du bruit de fond
        
        # Stopper si l'utilisateur s'arrête de parler plus de 1.5s
        if silent_chunks > int(silence_duration / chunk_duration):
            raise sd.CallbackStop()

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', 
                            device=device, blocksize=chunk_size, callback=callback):
            while True: sd.sleep(100)
    except Exception as e:
        pass # Expected when CallbackStop is raised

    print("\n✅ Silence détecté. Fin de l'enregistrement.")
    
    start_transcription_time = time.time()
    print(f"⏱️ Chronomètre démarré... Lancement de Whisper...")
    
    # 1. Sauvegarder le fichier
    filename = "test_record.wav"
    audio_data = np.concatenate(buffer, axis=0).flatten()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    # 2. Transcrire
    try:
        result = subprocess.run(
            ["./whisper.cpp/build/bin/whisper-cli", "-m", "./whisper.cpp/models/ggml-base.bin", "-l", "fr", "-nt", "-f", filename],
            capture_output=True, text=True
        )
        end_transcription_time = time.time()
        
        transcription = ""
        if result.stdout.strip():
            clean_text = re.sub(r'\[.*?\]|\( *? \)', '', result.stdout.strip()).strip()
            if clean_text:
                lines = clean_text.split('\n')
                transcription = lines[-1].strip()
        
        print("\n" + "="*50)
        print(f"👂 J'ai entendu : '{transcription}'")
        print(f"⏱️ Temps de transcription total : {end_transcription_time - start_transcription_time:.2f} secondes.")
        print("="*50)
        
    except Exception as e:
        print(f"Erreur Transcription: {e}")

if __name__ == "__main__":
    record_and_transcribe()
