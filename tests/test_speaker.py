import sounddevice as sd
import numpy as np
import time

def test_speaker():
    print("Recherche de tous les périphériques audio...")
    devices = sd.query_devices()
    
    # 1) Trouver l'enceinte USB
    output_device = None
    for i, dev in enumerate(devices):
        if dev['max_output_channels'] > 0 and ('USB' in dev['name'] or 'Audio' in dev['name']):
            output_device = dev['name'] # Utiliser le nom brut est beaucoup plus sûr sur sounddevice
            print(f"✅ Enceinte trouvée : {dev['name']}")
            break
            
    if not output_device:
        print("❌ Aucune enceinte USB trouvée.")
        return
        
    # 2) Générer un son de test (un bip doux à 440Hz / un La)
    print("Génération du son de test...")
    sample_rate = 44100
    duration = 2.0  # secondes
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Génère une onde sinusoïdale (bip)
    note = np.sin(440 * t * 2 * np.pi)
    
    # Convertit en int16 et réduit un peu le volume pour pas faire mal aux oreilles
    audio_data = (note * 15000).astype(np.int16)
    
    # 3) Jouer le son
    print(f"🔊 Lecture du son sur {output_device} en cours (2 secondes)...")
    try:
        sd.play(audio_data, samplerate=sample_rate, device=output_device)
        sd.wait() # Attend la fin du bip
        print("✅ Lecture terminée !")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture sur {output_device} : {e}")
        
if __name__ == "__main__":
    test_speaker()
