import subprocess
import os

# Chemins relatifs depuis la racine du projet vers les binaires et modèles Whisper
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHISPER_BIN = os.path.join(PROJECT_ROOT, "whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL = os.path.join(PROJECT_ROOT, "whisper.cpp/models/ggml-base.bin")

def transcribe_audio(audio_file_path):
    """
    Prend un fichier audio (.wav 16kHz) et retourne le texte transcrit via Whisper.
    """
    if not os.path.exists(audio_file_path):
        print(f"[ERREUR STT] Fichier audio introuvable : {audio_file_path}")
        return ""
        
    import time
    print(f"\n[STT] Transcription en cours de '{os.path.basename(audio_file_path)}'...")
    
    try:
        # Commande Whisper
        cmd = [
            WHISPER_BIN, 
            "-m", WHISPER_MODEL, 
            "-f", audio_file_path, 
            "-l", "fr",  # Langue française forcée pour plus de rapidité
            "-nt"        # Pas de timestamps (juste le texte brut)
        ]
        
        t0 = time.time()
        # Exécution silencieuse, on capte juste la sortie (stdout)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        t1 = time.time()
        
        # On nettoie la sortie (espaces en trop, sauts de ligne)
        text = result.stdout.strip()
        print(f"⏱️  [TEMPS] Whisper (STT) a transcrit en {t1 - t0:.2f}s")
        
        import re
        
        # Nettoyage des espaces
        text_clean = text.strip()
        
        # Mots ou expressions hallucinées fréquents quand il y a du silence/bruit
        blacklist = [
            "merci", "sous-titres", "sous-titrage", "amara.org",
            "musique", "silence", "rires", "rire", "toux", "soupir", "bruit", "audio",
            "cris de la pêche", "cris de l'âge"
        ]
        
        # On enlève la ponctuation et les balises pour vérifier le contenu textuel brut
        text_brut = re.sub(r'[^\w\s]', '', text_clean).lower().strip()
        
        # Si la phrase ne contient QUE un de ces mots/expressions parasites, on ignore
        if text_brut in blacklist:
            return ""
            
        if text_clean:
            print(f"[STT SUCCÈS] : {text_clean}")
        else:
            print("[STT] (Aucun texte détecté)")
            
        return text_clean
        
    except subprocess.TimeoutExpired:
        print("[ERREUR STT] Temps de transcription dépassé (15s).")
        return ""
    except Exception as e:
        print(f"[ERREUR STT] Problème lors de la transcription : {e}")
        return ""

if __name__ == "__main__":
    # Zone de test : On va utiliser le fichier qu'on vient d'enregistrer avec le micro !
    test_file = os.path.join(PROJECT_ROOT, "agent-v2", "tests-micro", "test-micro.wav")
    
    print("\n--- TEST DU MODULE SPEECH-TO-TEXT ---")
    if os.path.exists(test_file):
        texte_transcrit = transcribe_audio(test_file)
        print(f"\nRésultat final retourné par la fonction : '{texte_transcrit}'")
    else:
        print(f"[ATTENTION] Le fichier {test_file} n'existe pas. Veuillez d'abord utiliser micro.py pour enregistrer un test.")
