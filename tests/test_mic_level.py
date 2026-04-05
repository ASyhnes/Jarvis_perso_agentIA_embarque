import sounddevice as sd
import numpy as np

def test_mic():
    print("Recherche des périphériques d'entrée...")
    devices = sd.query_devices()
    input_device = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ('USB' in dev['name'] or 'Audio' in dev['name']):
            input_device = dev['name']  # On utilise le nom brut
            print(f"✅ Micro USB trouvé : {dev['name']}")
            break
            
    if not input_device:
        print("❌ Aucun micro USB trouvé.")
        return
        
    samplerate = 44100
    chunk_size = int(samplerate * 0.05)
    
    print(f"🎤 Écoute en cours sur {input_device}... Parlez pour voir le niveau !")
    print("Appuyez sur Ctrl+C pour arrêter.")
    print("-" * 50)
    
    def callback(indata, frames, time, status):
        # Appliquer le même gain logiciel (x5) que dans agent.py
        float_data = indata.astype(np.float32) * 5.0
        np.clip(float_data, -32768, 32767, out=float_data)
        boosted = float_data.astype(np.int16)
        
        # Calcul du volume RMS réel
        rms_volume = np.sqrt(np.mean(boosted.astype(np.float32)**2))
        
        # Affichage barre de volume
        bars = "=" * int(min(rms_volume / 50, 60))
        print(f"\r[Vol RMS: {rms_volume:7.1f}] {bars:<60}", end="", flush=True)

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', 
                            device=input_device, blocksize=chunk_size, callback=callback):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n✅ Arrêt du test.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    test_mic()
