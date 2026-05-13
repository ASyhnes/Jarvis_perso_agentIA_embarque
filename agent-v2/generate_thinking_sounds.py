#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les sons de patience pour Jarvis
Ces sons sont joués pendant que l'IA réfléchit
"""

import os
import subprocess
import sys

# Configuration
PIPER_BINARY = os.path.expanduser("~/piper_bin/piper")
VOICE_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "piper", "fr_FR-siwis-low.onnx")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thinking_sounds")

# Phrases de patience variées
PHRASES = [
    "Hmm, laisse moi réfléchir",
    "Un instant",
    "Je cherche",
    "Voyons voir",
    "Hmm",
    "Réflexion en cours",
    "J'y réfléchis",
    "Un moment",
]

def check_piper():
    """Vérifie que Piper est installé"""
    if not os.path.exists(PIPER_BINARY):
        print(f"❌ Erreur: Piper non trouvé à {PIPER_BINARY}")
        print("💡 Installez Piper ou ajustez PIPER_BINARY dans ce script")
        return False
    
    if not os.path.exists(VOICE_MODEL):
        print(f"❌ Erreur: Modèle vocal non trouvé à {VOICE_MODEL}")
        print("💡 Vérifiez que le modèle Piper est bien installé")
        return False
    
    return True

def generate_sounds():
    """Génère les fichiers audio"""
    # Créer le dossier si nécessaire
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("🔊 Génération des sons de patience...")
    print(f"📁 Dossier: {OUTPUT_DIR}")
    print(f"🎤 Modèle: {VOICE_MODEL}")
    print("")
    
    success_count = 0
    
    for i, phrase in enumerate(PHRASES, 1):
        output_file = os.path.join(OUTPUT_DIR, f"thinking_{i}.wav")
        
        print(f"[{i}/{len(PHRASES)}] Génération: '{phrase}'... ", end="", flush=True)
        
        try:
            # Générer avec Piper
            result = subprocess.run(
                [PIPER_BINARY, "--model", VOICE_MODEL, "--output_file", output_file],
                input=phrase.encode('utf-8'),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                print("✅")
                success_count += 1
            else:
                print("❌")
                print(f"   Erreur: {result.stderr.decode('utf-8')}")
        
        except subprocess.TimeoutExpired:
            print("❌ (timeout)")
        except Exception as e:
            print(f"❌ ({e})")
    
    print("")
    print("="*60)
    print(f"✅ {success_count}/{len(PHRASES)} sons générés avec succès")
    print("="*60)
    
    if success_count > 0:
        print("\n💡 Ces sons seront joués aléatoirement pendant que Jarvis réfléchit !")
        print(f"📂 Fichiers dans: {OUTPUT_DIR}")
    
    return success_count > 0

def main():
    print("\n" + "🎵 " * 30)
    print("   GÉNÉRATION DES SONS DE PATIENCE")
    print("🎵 " * 30)
    print("")
    
    # Vérifications
    if not check_piper():
        return 1
    
    # Génération
    if generate_sounds():
        print("\n✅ Terminé ! Relancez Jarvis pour entendre les sons.")
        return 0
    else:
        print("\n❌ Échec de la génération des sons")
        return 1

if __name__ == "__main__":
    sys.exit(main())
