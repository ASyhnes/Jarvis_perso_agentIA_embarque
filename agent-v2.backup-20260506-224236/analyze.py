import wave
import numpy as np
import scipy.signal
import os

def analyze_audio(file_path):
    if not os.path.exists(file_path):
        print(f"Fichier non trouvé: {file_path}")
        return

    print(f"--- ANALYSE DE {file_path} ---")
    with wave.open(file_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        
        print(f"Canaux: {n_channels}")
        print(f"Largeur (bytes): {sampwidth}")
        print(f"Fréquence: {framerate} Hz")
        print(f"Durée: {n_frames / framerate:.2f} secondes")
        
        data = wf.readframes(n_frames)
        
    # Convertir en array numpy
    audio_data = np.frombuffer(data, dtype=np.int16)
    
    # Paramètres d'analyse
    block_size = framerate // 10  # 100ms blocks
    num_blocks = len(audio_data) // block_size
    
    rms_values = []
    
    for i in range(num_blocks):
        start = i * block_size
        end = start + block_size
        block = audio_data[start:end]
        rms = np.sqrt(np.mean(block.astype(np.float64)**2))
        rms_values.append(rms)

    print("\n--- STATISTIQUES GLOBALES ---")
    print(f"Volume Max (Crête brut): {np.max(np.abs(audio_data))}")
    print(f"Volume Moyen (Bruit de fond estimé RMS): {np.median(rms_values):.1f}")
    print(f"Volume Max RMS (Voix la plus forte estimée): {np.max(rms_values):.1f}")
    
    # Détection basique des pics de voix
    print("\n--- DÉTECTION DES PRISES DE PAROLE ---")
    # On considère qu'on parle si le RMS dépasse 3x la médiane (bruit de fond heuristique)
    threshold = max(200, np.median(rms_values) * 3) 
    print(f"Seuil de parole utilisé pour l'analyse: {threshold:.1f}")
    
    is_speaking = False
    speech_start = 0
    speech_events = []
    
    for i, rms in enumerate(rms_values):
        time_sec = i * (block_size/framerate)
        
        if rms > threshold and not is_speaking:
            is_speaking = True
            speech_start = time_sec
        elif rms < threshold and is_speaking:
            is_speaking = False
            duration = time_sec - speech_start
            if duration > 0.5: # Ignorer les bruits ultra courts (<0.5s)
                # Trouver le pic RMS pendant cette période
                start_idx = int(speech_start * framerate / block_size)
                end_idx = i
                peak_rms = np.max(rms_values[start_idx:end_idx])
                
                speech_events.append({
                    "start": speech_start,
                    "end": time_sec,
                    "duration": duration,
                    "peak_rms": peak_rms
                })
                
    for idx, event in enumerate(speech_events):
        print(f"Événement vocal {idx+1}: De {event['start']:.1f}s à {event['end']:.1f}s (Durée: {event['duration']:.1f}s) - Volume Pic RMS: {event['peak_rms']:.1f}")

if __name__ == '__main__':
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests-micro", "test-micro.wav")
    analyze_audio(target)
