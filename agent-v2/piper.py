import subprocess
import os
import sounddevice as sd
import numpy as np

# Import du module speaker pour récupérer l'index de l'enceinte
try:
    from speaker import get_speaker_index
except ImportError:
    pass
    
try:
    from state import BotStates
except ImportError:
    pass

# Chemins depuis la racine du projet
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPER_BINARY = os.path.expanduser("~/piper_bin/piper")
VOICE_MODEL = os.path.join(PROJECT_ROOT, "piper/fr_FR-siwis-low.onnx")

def speak(text, device_idx=None, state_manager=None):
    """
    Transforme le texte en voix avec Piper, puis joue le son sur le périphérique audio (enceinte).
    :param text: Texte à lire
    :param device_idx: Index de l'enceinte (récupéré par speaker.py)
    :param state_manager: Permet de synchroniser l'animation quand le son sort réellement
    """
    if not text.strip():
        return
        
    print(f"\n[TTS] Génération de la voix : '{text}'")
    
    if not os.path.exists(PIPER_BINARY):
        print(f"[ERREUR TTS] Binaire Piper introuvable : {PIPER_BINARY}")
        return
    if not os.path.exists(VOICE_MODEL):
        print(f"[ERREUR TTS] Modèle de voix introuvable : {VOICE_MODEL}")
        return
        
    try:
        # Popen lance le processus en parallèle, on communique avec lui via stdin/stdout
        proc = subprocess.Popen(
            [PIPER_BINARY, "--model", VOICE_MODEL, "--output-raw"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        # On envoie le texte au processus, et on récupère l'audio brut en sortie
        stdout, _ = proc.communicate(input=text.encode('utf-8'))
        
        # Le flux brut est converti en tableau int16 pour sounddevice
        import numpy as np
        audio_data = np.frombuffer(stdout, dtype=np.int16)
        
        # Le modèle fr_FR-siwis génère l'audio en 22050 Hz.
        # On déclenche l'animation de bouche AU MOMENT où le son va sortir
        if state_manager:
            state_manager.set(BotStates.SPEAKING)
            
        # On lit le son sur l'enceinte
        import sounddevice as sd
        sd.play(audio_data, 22050, device=device_idx)
        sd.wait() # Attendre la fin de la phrase
        
    except Exception as e:
        print(f"[ERREUR TTS] Problème lors de la synthèse vocale : {e}")

if __name__ == "__main__":
    print("\n--- TEST DU MODULE TEXT-TO-SPEECH ---")
    
    # Récupération de l'index de l'enceinte
    idx = get_speaker_index()
    
    if idx is not None:
        phrase_test = "Bonjour, je suis l'agent V2. Ma synthèse vocale fonctionne parfaitement bien."
        speak(phrase_test, idx)
    else:
        print("[ATTENTION] Enceinte non trouvée, je ne peux pas jouer la voix.")
