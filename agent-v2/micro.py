import sounddevice as sd
import numpy as np
import time
import wave
import os
import scipy.signal

from whisper import transcribe_audio

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("[ERREUR] Veuillez installer matplotlib : pip install matplotlib")
    plt = None

# Dossier courant pour y enregistrer les fichiers de test
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(CURRENT_DIR, "tests-micro")

if not os.path.exists(TESTS_DIR):
    os.makedirs(TESTS_DIR)

def get_micro_index():
    devices = sd.query_devices()
    print("\n--- SCAN DES PÉRIPHÉRIQUES D'ENTRÉE (MICRO) ---")
    
    for i, dev in enumerate(devices):
        if "USB PnP Sound Device" in dev['name'] and dev['max_input_channels'] > 0:
            print(f"[SYSTEM] MICRO trouvé à l'index {i} : {dev['name']}")
            return i
            
    print("[ERREUR] Micro non trouvé.")
    return None

def calibrate_micro(device_idx, duration=30, fs=16000):
    if device_idx is None:
        print("Impossible de calibrer sans micro.")
        return
        
    print(f"\n--- DÉBUT DE LA CALIBRATION ({duration} secondes) ---")
    print("Veuillez dire : 'Hello, je m'appelle david, hey jarvis !'")
    print("Puis parlez normalement, faites du silence, baissez ou augmentez la voix...")
    
    # Prépare l'enregistrement avec le format natif du micro
    info = sd.query_devices(device_idx, 'input')
    native_fs = int(info['default_samplerate'])
    print(f"[INFO] Fréquence native du micro : {native_fs}Hz. Enregistrement en cours...", end="")
    
    try:
        # sd.rec lance l'enregistrement en arrière-plan à la fréquence NATIVE globale (ex: 48000Hz)
        recording = sd.rec(int(duration * native_fs), samplerate=native_fs, channels=1, dtype='int16', device=device_idx)
        
        # Affichage d'une petite barre de progression dans la console
        for i in range(duration):
            time.sleep(1)
            print(".", end="", flush=True)
            
        sd.wait() # Attendre la fin réelle
        print("\nEnregistrement terminé !")
        
        # Conversion du tableau 2D (N, 1) en tableau 1D
        audio_data = recording.flatten()

        # Whisper et notre application ont besoin de 16000 Hz. On ré-échantillonne si nécessaire
        if native_fs != fs:
            import scipy.signal
            num_samples = int(len(audio_data) * fs / native_fs)
            audio_data = scipy.signal.resample(audio_data, num_samples).astype(np.int16)
            print(f"[INFO] Audio converti en {fs}Hz.")

        # Sauvegarde de l'audio dans un fichier WAV
        wav_path = os.path.join(TESTS_DIR, "test-micro.wav")
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())
        print(f"Fichier audio sauvegardé sous : {wav_path}")
        
        if plt is None:
            print("Graphique impossible (matplotlib non installé).")
            return
            
        # Conversion du tableau 2D (N, 1) en tableau 1D
        audio_data = recording.flatten()
        
        # Création de l'axe temporel
        times = np.linspace(0, duration, num=len(audio_data))
        
        # Calcul du volume RMS (fenêtré) pour voir l'enveloppe sonore
        # On regroupe par blocs de 1/10 de seconde par exemple
        block_size = fs // 10
        num_blocks = len(audio_data) // block_size
        
        rms_values = []
        rms_times = []
        for i in range(num_blocks):
            start = i * block_size
            end = start + block_size
            block = audio_data[start:end]
            # Calcul RMS manuel (plus sûr que la std si moyenne != 0)
            rms = np.sqrt(np.mean(block.astype(np.float64)**2))
            rms_values.append(rms)
            rms_times.append(start / fs)
            
        plt.figure(figsize=(12, 6))
        
        # Graphique 1 : Forme d'onde brute
        plt.subplot(2, 1, 1)
        plt.plot(times, audio_data, color='blue', alpha=0.5)
        plt.title("Forme d'onde brute (Amplitude sur 16 bits)")
        plt.xlabel("Temps (secondes)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        # Graphique 2 : Volume RMS (Idéal pour le seuil)
        plt.subplot(2, 1, 2)
        plt.plot(rms_times, rms_values, color='red')
        plt.title("Enveloppe du volume RMS (Pour déterminer le seuil d'écoute)")
        plt.xlabel("Temps (secondes)")
        plt.ylabel("Volume (RMS)")
        plt.grid(True)
        
        # Ajoutons des lignes de test pour le seuil
        plt.axhline(y=200, color='g', linestyle='--', label='Seuil Actuel (200)')
        plt.axhline(y=500, color='orange', linestyle='--', label='Seuil (500)')
        plt.axhline(y=1000, color='r', linestyle='--', label='Seuil (1000)')
        plt.legend()
        
        plt.tight_layout()
        
        # Sauvegarde du graphique dans une image
        img_path = os.path.join(TESTS_DIR, "test-micro.png")
        plt.savefig(img_path)
        print(f"Graphique sauvegardé sous : {img_path}")
        
        print("\nFermez la fenêtre du graphique pour terminer le script.")
        plt.show()
        
    except Exception as e:
        print(f"\n[ERREUR LORS DE L'ENREGISTREMENT] : {e}")

def listen_continuously(device_idx, threshold=450, target_fs=16000, on_transcription=None, state_manager=None):
    """
    Écoute en boucle de manière continue via un Flux (Stream). 
    Enregistre l'audio uniquement quand le volume dépasse le seuil (threshold) 
    et s'arrête après un temps de silence.
    Le fichier est ensuite envoyé automatiquement vers Whisper pour transcription.
    """
    if device_idx is None:
        return
        
    info = sd.query_devices(device_idx, 'input')
    native_fs = int(info['default_samplerate'])
    
    # On paramètre des blocs très courts (ex: 0.25 secondes) pour réagir vite
    chunk_duration = 0.25
    chunk_samples = int(chunk_duration * native_fs)
    max_silence_chunks = 6 # 6 * 0.25s = 1.5s de silence maximum avant de couper l'enregistrement
    
    is_recording = False
    audio_buffer = []
    silence_chunks = 0
    pre_listening_state = None
    
    # On ouvre un Stream qui tourne en tâche de fond continue
    stream = sd.InputStream(samplerate=native_fs, device=device_idx, channels=1, dtype='int16')
    stream.start()
    
    print(f"\n[ÉCOUTE] Micro activé (Seuil RMS={threshold}). En attente critique...")
    print("Dites quelque chose... (Appuyez sur Ctrl+C pour arrêter le programme)\n")
    
    try:
        while True:
            # On lit le micro bloc par bloc (bloquant jusqu'à ce que 0.25s soit écoulé)
            chunk, overflow = stream.read(chunk_samples)
            if overflow:
                continue
                
            mono_chunk = chunk.flatten()
            rms = np.sqrt(np.mean(mono_chunk.astype(np.float64)**2))
            
            # Si le volume dépasse notre seuil...
            if rms > threshold:
                if not is_recording:
                    pre_listening_state = state_manager.current if state_manager else None
                    if state_manager: state_manager.set("listening")
                    print("\n[DETECT] Voix détectée ! Début de l'enregistrement...")
                    is_recording = True
                    audio_buffer = [mono_chunk]
                    silence_chunks = 0
                else:
                    audio_buffer.append(mono_chunk)
                    silence_chunks = 0
            # Si le volume est bas...
            else:
                if is_recording:
                    audio_buffer.append(mono_chunk)
                    silence_chunks += 1
                    
                    # Si le silence dure depuis un moment, la phrase est finie !
                    if silence_chunks >= max_silence_chunks:
                        print("[DETECT] Silence prolongé détecté. Fin de la phrase.")
                        is_recording = False
                        
                        # Assembler tous les morceaux en un seul fichier audio
                        full_audio = np.concatenate(audio_buffer)
                        total_duration = len(full_audio) / native_fs
                        
                        # Si l'audio est trop court (ex: un claquement de porte), on l'ignore
                        if total_duration > 1.0: 
                            # Convertir la fréquence pour Whisper (16000 Hz)
                            if native_fs != target_fs:
                                num_samples = int(len(full_audio) * target_fs / native_fs)
                                audio_ready = scipy.signal.resample(full_audio, num_samples).astype(np.int16)
                            else:
                                audio_ready = full_audio
                                
                            # Sauvegarder temporellement
                            wav_path = os.path.join(TESTS_DIR, "input.wav")
                            with wave.open(wav_path, "wb") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(target_fs)
                                wf.writeframes(audio_ready.tobytes())
                            
                            # === APPEL DE WHISPER ===
                            if state_manager: state_manager.set("thinking")
                            print("Transmission de l'audio à Whisper...")
                            transcription = transcribe_audio(wav_path)
                            
                            if transcription:
                                print("\n=============================================")
                                print(f"🎤 VOUS AVEZ DIT : {transcription}")
                                print("=============================================\n")
                                
                                # Si le main.py écoute, on lui passe le texte
                                if on_transcription:
                                    on_transcription(transcription)
                            else:
                                print("[INFO] Silence ou bruit parasite (filtré par Whisper).")
                                if state_manager: state_manager.set(pre_listening_state or "idle")
                            
                        else:
                            print("[INFO] Bruit parasite ignoré (trop court).")
                            if state_manager: state_manager.set(pre_listening_state or "idle")
                            
                        # Vider la mémoire pour écouter la prochaine phrase
                        audio_buffer = []
                        
                        # Si l'état est toujours "thinking" (ex: phrase neutre ignorée par wakeword)
                        # On restaure l'état qu'il y avait avant de parler (SLEEP ou IDLE).
                        if state_manager and state_manager.current == "thinking":
                            state_manager.set(pre_listening_state or "idle")
                            
                        print("[ÉCOUTE] En attente de la prochaine prise de parole...")
                        
    except KeyboardInterrupt:
        print("\n[SYSTEM] Fin de l'écoute demandée par l'utilisateur.")
    finally:
        stream.stop()
        stream.close()

if __name__ == "__main__":
    idx = get_micro_index()
    if idx is not None:
        print(f"Index à utiliser pour l'enregistrement : {idx}")
        # Si tu veux relancer une calibration un jour, décommente la ligne suivante :
        # calibrate_micro(idx, duration=30)
        
        # Lancement de l'écoute continue
        listen_continuously(idx, threshold=450)
