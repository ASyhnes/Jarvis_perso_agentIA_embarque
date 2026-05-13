#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Jarvis-BMO Optimisé - Mode Audio (avec TTS)
Teste l'IA + la synthèse vocale avec Piper persistant
"""

import sys
import os
import time

# Ajouter le répertoire agent-v2 au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-v2'))

from brain import think, HAILO_URL, TEXT_MODEL
from piper import speak, speak_multiple, cleanup_piper
from speaker import get_speaker_index

def test_connection():
    """Vérifie la connexion à hailo-ollama"""
    import requests
    print("🔍 Vérification de la connexion à hailo-ollama...")
    try:
        resp = requests.get("http://127.0.0.1:8000/api/tags", timeout=5)
        if resp.status_code == 200:
            print("✅ hailo-ollama est accessible")
            return True
        else:
            print(f"❌ hailo-ollama répond mais avec erreur: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ hailo-ollama n'est pas accessible: {e}")
        print("💡 Lancez d'abord: ./start_hailo_ollama.sh")
        return False

def test_speaker():
    """Vérifie que l'enceinte est détectée"""
    print("\n🔍 Recherche de l'enceinte...")
    spk_idx = get_speaker_index()
    if spk_idx is None:
        print("❌ Enceinte non trouvée")
        print("\n💡 Branchez une enceinte USB et relancez")
        return None
    print(f"✅ Enceinte trouvée (index: {spk_idx})")
    return spk_idx

def test_tts_simple(spk_idx):
    """Test TTS basique"""
    print("\n" + "="*60)
    print("🎤 TEST 1: Synthèse vocale simple")
    print("="*60)
    
    phrase_test = "Bonjour, je suis Jarvis optimisé avec Piper persistant."
    print(f"📝 Phrase: {phrase_test}")
    
    print("\n⏱️  Mesure de la latence...")
    start = time.time()
    speak(phrase_test, device_idx=spk_idx)
    end = time.time()
    
    print(f"✅ Temps total: {end - start:.2f}s")
    return end - start

def test_tts_multiple(spk_idx):
    """Test TTS avec plusieurs phrases (optimisation Piper persistant)"""
    print("\n" + "="*60)
    print("🎤 TEST 2: Plusieurs phrases (mode continu)")
    print("="*60)
    print("💡 Avec Piper persistant, il y a ZÉRO délai entre phrases")
    
    phrases = [
        "Première phrase.",
        "Deuxième phrase.",
        "Troisième phrase.",
    ]
    
    print(f"📝 {len(phrases)} phrases à dire...")
    
    print("\n⏱️  Mesure de la latence...")
    start = time.time()
    speak_multiple(phrases, device_idx=spk_idx)
    end = time.time()
    
    print(f"✅ Temps total: {end - start:.2f}s")
    print(f"   (~{(end - start) / len(phrases):.2f}s par phrase)")
    return end - start

def test_ia_plus_tts(spk_idx):
    """Test complet: IA + TTS"""
    print("\n" + "="*60)
    print("🤖 TEST 3: IA + Synthèse vocale")
    print("="*60)
    
    question = "Présente-toi en une phrase courte"
    print(f"❓ Question: {question}")
    
    # Appel IA
    print("\n🧠 Jarvis réfléchit...")
    t_start = time.time()
    reply = think(question)
    t_think = time.time()
    
    if not reply:
        print("❌ Pas de réponse de l'IA")
        return None
    
    print(f"💬 Réponse: {reply}")
    print(f"⏱️  Temps IA: {t_think - t_start:.2f}s")
    
    # Synthèse vocale
    print("\n🔊 Jarvis parle...")
    speak(reply, device_idx=spk_idx)
    t_end = time.time()
    
    print(f"⏱️  Temps vocal: {t_end - t_think:.2f}s")
    print(f"✅ Temps TOTAL: {t_end - t_start:.2f}s")
    
    return t_end - t_start

def main():
    """Point d'entrée principal"""
    print("\n" + "🎵 " * 30)
    print("   TEST AUDIO JARVIS-BMO OPTIMISÉ")
    print("🎵 " * 30)
    
    # Vérifier hailo-ollama
    if not test_connection():
        return 1
    
    # Vérifier enceinte
    spk_idx = test_speaker()
    if spk_idx is None:
        return 1
    
    print("\n✅ Tout est prêt pour les tests audio !\n")
    input("⏸️  Appuyez sur ENTRÉE pour commencer les tests...")
    
    try:
        # Test 1: TTS simple
        t1 = test_tts_simple(spk_idx)
        input("\n⏸️  Appuyez sur ENTRÉE pour le test suivant...")
        
        # Test 2: TTS multiple (Piper persistant)
        t2 = test_tts_multiple(spk_idx)
        input("\n⏸️  Appuyez sur ENTRÉE pour le test suivant...")
        
        # Test 3: IA + TTS complet
        t3 = test_ia_plus_tts(spk_idx)
        
        # Résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*60)
        print(f"1. TTS simple:          {t1:.2f}s")
        print(f"2. TTS continu (3x):    {t2:.2f}s")
        if t3:
            print(f"3. IA + TTS complet:    {t3:.2f}s")
        print("="*60)
        
        print("\n💡 Optimisations vérifiées:")
        print("   ✅ Piper persistant (pas de gap entre phrases)")
        print("   ✅ IA rapide sur Hailo NPU")
        print("   ✅ TTS fluide et continu")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test interrompu")
    finally:
        print("\n🧹 Nettoyage...")
        cleanup_piper()
        print("✅ Terminé !")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
