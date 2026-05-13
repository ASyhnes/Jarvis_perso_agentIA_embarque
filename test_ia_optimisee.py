#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Jarvis-BMO Optimisé - Mode Console (Texte uniquement)
Permet de tester l'IA sans audio ni interface graphique
"""

import sys
import os

# Ajouter le répertoire agent-v2 au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-v2'))

from brain import think, conversation_history, HAILO_URL, TEXT_MODEL

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

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("🤖 TEST JARVIS-BMO OPTIMISÉ - Mode Console")
    print("="*60)
    print(f"📡 URL: {HAILO_URL}")
    print(f"🧠 Modèle: {TEXT_MODEL}")
    print(f"💾 Historique: {len(conversation_history)} messages en mémoire")
    print("="*60)
    print("\nCommandes:")
    print("  - Tapez votre question et ENTRÉE pour discuter")
    print("  - 'historique' pour voir l'historique")
    print("  - 'reset' pour vider l'historique")
    print("  - 'quit' ou 'exit' pour quitter")
    print("="*60)

def afficher_historique():
    """Affiche l'historique de conversation"""
    if not conversation_history:
        print("\n📝 Historique vide")
        return
    
    print("\n📝 HISTORIQUE DE CONVERSATION")
    print("-" * 60)
    for i, msg in enumerate(conversation_history, 1):
        role = "👤 VOUS" if msg['role'] == 'user' else "🤖 JARVIS"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{i}. {role}: {content}")
    print("-" * 60)

def reset_historique():
    """Vide l'historique"""
    global conversation_history
    from brain import conversation_history as ch
    ch.clear()
    print("🗑️  Historique vidé")

def chat_loop():
    """Boucle de chat interactive"""
    afficher_menu()
    
    while True:
        try:
            # Prompt
            user_input = input("\n💬 Vous: ").strip()
            
            if not user_input:
                continue
            
            # Commandes spéciales
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir !")
                break
            
            if user_input.lower() == 'historique':
                afficher_historique()
                continue
            
            if user_input.lower() == 'reset':
                reset_historique()
                continue
            
            if user_input.lower() == 'menu':
                afficher_menu()
                continue
            
            # Appel à l'IA optimisée
            print("\n🤖 Jarvis réfléchit...", end="", flush=True)
            reply = think(user_input)
            print("\r" + " " * 30 + "\r", end="")  # Efface le message
            
            if reply:
                print(f"🤖 Jarvis: {reply}")
            else:
                print("❌ Pas de réponse (vérifiez que hailo-ollama tourne)")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interruption détectée. Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Point d'entrée principal"""
    print("\n" + "🚀 " * 30)
    print("   TEST JARVIS-BMO OPTIMISÉ - HAILO NPU")
    print("🚀 " * 30)
    
    # Vérifier la connexion
    if not test_connection():
        print("\n⚠️  Impossible de continuer sans hailo-ollama")
        print("\n💡 Dans un autre terminal, lancez:")
        print("   cd /home/syhnes/be-more-agent")
        print("   ./start_hailo_ollama.sh")
        return 1
    
    print("\n✅ Tout est prêt !\n")
    
    # Exemples de questions
    print("💡 Exemples de questions à tester:")
    print("   - Présente-toi en une phrase")
    print("   - Quelle est la capitale de la France ?")
    print("   - Explique-moi ce qu'est un NPU")
    print("   - Raconte-moi une blague courte")
    
    # Lancer le chat
    chat_loop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
