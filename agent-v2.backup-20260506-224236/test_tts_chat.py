"""
Test interactif : Chat terminal + TTS (Piper) — gemma3:1b
----------------------------------------------------------
Au démarrage : nettoie tous les modèles Ollama chargés
et relance un service propre avant la première conversation.
Tape ton message, l'IA répond en texte ET en voix.
Tape 'quitter' ou 'exit' pour arrêter.
"""

import sys
import os
import time
import subprocess

# S'assurer que les imports trouvent les modules du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speaker import get_speaker_index
from piper import speak

# ─── Configuration ────────────────────────────────────────────────────────────
TEXT_MODEL = "gemma3:1b"


# ─── Nettoyage et redémarrage d'Ollama ────────────────────────────────────────
def reset_ollama():
    """Décharge tous les modèles en cours et redémarre le service Ollama proprement."""
    print("\n[INIT] Nettoyage d'Ollama en cours...")

    # 1. Récupérer les modèles chargés
    try:
        result = subprocess.run(
            ["ollama", "ps"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().splitlines()
        # La première ligne est l'en-tête, on la saute
        model_names = [line.split()[0] for line in lines[1:] if line.strip()]
        for model in model_names:
            print(f"[INIT] Déchargement de '{model}'...")
            subprocess.run(["ollama", "stop", model], timeout=10)
    except Exception as e:
        print(f"[INIT] Avertissement lors du déchargement des modèles : {e}")

    # 2. Arrêter le service Ollama
    print("[INIT] Arrêt du service Ollama...")
    subprocess.run(["sudo", "systemctl", "stop", "ollama"], timeout=15)
    time.sleep(2)

    # 3. Relancer un service propre
    print("[INIT] Démarrage d'un service Ollama propre...")
    subprocess.run(["sudo", "systemctl", "start", "ollama"], timeout=15)
    time.sleep(3)  # Laisser le temps au service de démarrer

    print(f"[INIT] Ollama prêt. Modèle cible : {TEXT_MODEL}\n")


# ─── LLM ──────────────────────────────────────────────────────────────────────
def think(user_text, conversation_history, ollama_client):
    """Interroge le LLM et retourne la réponse textuelle."""
    if not user_text.strip():
        return "", conversation_history

    print(f"\n[LLM] Réflexion sur : '{user_text}' ...")

    try:
        messages = list(conversation_history)
        messages.append({'role': 'user', 'content': user_text})

        response = ollama_client.chat(model=TEXT_MODEL, messages=messages)
        reply = response.get('message', {}).get('content', '')

        # Nettoyage du markdown résiduel
        reply = reply.replace("*", "").replace("#", "").replace("_", "")

        if reply:
            print(f"\n[IA] : {reply}")
            conversation_history.append({'role': 'user', 'content': user_text})
            conversation_history.append({'role': 'assistant', 'content': reply})
            # Garder les 10 derniers messages max
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
        else:
            print("[LLM] Aucune réponse générée.")

        return reply, conversation_history

    except Exception as e:
        print(f"[ERREUR LLM] Impossible de contacter Ollama : {e}")
        return "Désolé, j'ai rencontré un problème.", conversation_history


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Nettoyage et redémarrage propre d'Ollama
    reset_ollama()

    # Import du client Ollama APRÈS le redémarrage du service
    from ollama import Client
    ollama_client = Client(host='http://127.0.0.1:11434')

    print("=" * 52)
    print(f"  TEST CHAT + TTS — Modèle : {TEXT_MODEL}")
    print("  Tape 'quitter' ou 'exit' pour arrêter.")
    print("=" * 52)

    # Périphérique audio
    speaker_idx = get_speaker_index()
    if speaker_idx is None:
        print("\n[ATTENTION] Enceinte non trouvée. Le TTS sera muet.")
    else:
        print(f"\n[OK] Enceinte prête (index {speaker_idx}).\n")

    conversation_history = []

    while True:
        try:
            user_input = input("\nToi : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[INFO] Interruption. Au revoir !")
            break

        if not user_input:
            continue

        # ⚠️ Vérifier les commandes de sortie AVANT d'envoyer au LLM
        if user_input.lower().strip("/") in ("quitter", "exit", "quit", "bye"):
            print("[INFO] Fermeture du chat. À bientôt !")
            break

        # LLM
        response, conversation_history = think(user_input, conversation_history, ollama_client)

        if not response:
            continue

        # TTS
        speak(response, device_idx=speaker_idx)


if __name__ == "__main__":
    main()
