#!/usr/bin/env python3
"""
Script de test pour faire parler Jarvis
Message personnalisé pour Léo
"""

import sys
import os

# Ajouter le chemin vers agent-v2 pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-v2'))

from speaker import get_speaker_index
from piper import speak, cleanup_piper

if __name__ == "__main__":
    print("\n=== TEST JARVIS - MESSAGE POUR LÉO ===\n")
    
    # Message exact à dire
    message = "bonjour Léo, j'espère que tu vas bien. David m'a dit de te dire qu'il pense a toi"
    
    print(f"📝 Message à prononcer : '{message}'\n")
    
    # Récupération de l'index de l'enceinte
    speaker_idx = get_speaker_index()
    
    if speaker_idx is not None:
        print(f"🔊 Enceinte détectée (index: {speaker_idx})")
        print("🎙️  Jarvis va maintenant parler...\n")
        
        # Faire parler Jarvis
        speak(message, device_idx=speaker_idx)
        
        print("\n✅ Test terminé !")
        
        # Nettoyage
        cleanup_piper()
    else:
        print("❌ ERREUR: Aucune enceinte détectée.")
        print("Jarvis ne peut pas parler sans enceinte.")
        sys.exit(1)
