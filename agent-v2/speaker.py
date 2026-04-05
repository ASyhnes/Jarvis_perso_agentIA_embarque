import sounddevice as sd

def get_speaker_index():
    devices = sd.query_devices()
    print("\n--- SCAN DES PÉRIPHÉRIQUES DE SORTIE (ENCEINTE) ---")
    
    for i, dev in enumerate(devices):
        if "USB PnP Audio Device" in dev['name'] and dev['max_output_channels'] > 0:
            print(f"[SYSTEM] ENCEINTE trouvée à l'index {i} : {dev['name']}")
            return i
            
    print("[ERREUR] Enceinte non trouvée.")
    return None

if __name__ == "__main__":
    idx = get_speaker_index()
    if idx is not None:
        print(f"Index à utiliser pour la lecture : {idx}")
