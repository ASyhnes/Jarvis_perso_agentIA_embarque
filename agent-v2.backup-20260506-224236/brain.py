import requests
import json
import os
import re
from tool_registry import ToolRegistry

# Configuration du modèle et du client
TEXT_MODEL = "qwen2.5:1.5b"
# ✅ System prompt FIXE et court (ne change JAMAIS entre les requêtes)
SYSTEM_PROMPT = "Tu es Jarvis, un assistant vocal intelligent et sympathique. Tu réponds toujours en français, de manière très courte et naturelle."
# ✅ URL de l'API /chat (pas /generate)
HAILO_URL = "http://127.0.0.1:8000/api/chat"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(PROJECT_ROOT, "long_term_memory.txt")

# Mémoire à court terme (STM) : stocke la conversation de la session courante
conversation_history = []

_global_registry = None

def get_registry(ui_queue):
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry(ui_queue=ui_queue)
    return _global_registry


def get_long_term_memory():
    """Lit le fichier de mémoire à long terme s'il existe."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
    return ""


def strip_prompt_leakage(content: str) -> str:
    """Nettoyage avancé anti-hallucination (inspiré de be-more-hailo).
    
    Supprime :
    - Les blocs de réflexion <think>...</think> de Qwen2.5
    - Les marqueurs de template et placeholders
    - Les labels de ligne (Opinion:, Rule 1:, etc.)
    - Les listes numérotées au début des lignes
    """
    if not content:
        return ""
    
    # 1. Supprime les blocs de réflexion <think>...</think>
    if "<think>" in content.lower():
        if "</think>" in content.lower():
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL | re.IGNORECASE)
        else:
            # <think> non fermé : coupe tout après
            content = re.split(r'<think>', content, flags=re.IGNORECASE)[0]
    
    # 2. Extrait le contenu entre [JARVIS]...[/JARVIS] si présent
    if "[/JARVIS]" in content:
        m = re.search(r'\[JARVIS\](.*?)\[/JARVIS\]', content, flags=re.DOTALL | re.IGNORECASE)
        if m:
            content = m.group(1).strip()
    elif "[JARVIS]" in content:
        # Half-tagged : strip tout avant [JARVIS]
        content = content.split("[JARVIS]", 1)[1].strip()
    
    # 3. Supprime les labels de ligne (My thoughts:, Opinion:, Rule 1:, etc.)
    content = re.sub(
        r'^\s*(?:My thoughts|Reaction|Opinion|Mon avis|Ma pensée|Summarize|Résumé|Rule \d+|Règle \d+):\s*',
        '', content, flags=re.IGNORECASE | re.MULTILINE
    )
    
    # 4. Supprime les listes numérotées au début des lignes (1. 2. 3.)
    content = re.sub(r'^\s*\d+[\.\)]\s+', '', content, flags=re.MULTILINE)
    
    # 5. Supprime les placeholders template
    placeholders = [
        r'\[CUTE_WHIMSICAL_DESCRIPTION\]',
        r'\[DESCRIPTION\]',
        r'YOUR_PROMPT_HERE',
        r'\[Summarize[^\]]*\]',
    ]
    for pattern in placeholders:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # 6. Collapse runs of blank lines
    content = re.sub(r'\n{3,}', '\n\n', content).strip()
    
    return content


def think(user_text, ui_queue=None):
    """
    Prend le texte transcrit par Whisper et interroge l'IA (Ollama).
    Retourne la réponse textuelle complète de l'IA.
    
    ✅ Corrections appliquées :
    - API /chat au lieu de /generate
    - Format JSON structuré (pas de formatage ChatML manuel)
    - System prompt stable (LTM séparée)
    - Nettoyage anti-hallucination
    """
    if not user_text.strip():
        return ""

    print(f"\n[CERVEAU] Réflexion sur : '{user_text}' ...")

    try:
        global conversation_history
        
        # ✅ System prompt FIXE (ne change jamais)
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        
        # ✅ Ajout de l'historique de conversation
        messages.extend(conversation_history)
        
        # ✅ LTM injectée dans le MESSAGE UTILISATEUR (pas le system prompt)
        ltm = get_long_term_memory()
        if ltm:
            # Format : [Contexte: ...] suivi de la vraie question
            user_message = f"[Contexte: {ltm}]\n\n{user_text}"
        else:
            user_message = user_text
        
        messages.append({'role': 'user', 'content': user_message})
        
        # ✅ Payload JSON structuré pour l'API /chat
        payload = {
            "model": TEXT_MODEL,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        print("\n--- [DEBUG] MESSAGES ENVOYÉS À L'IA ---")
        for i, msg in enumerate(messages):
            role = msg['role']
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"{i}. {role}: {content}")
        print("------------------------------------\n")
        
        # ✅ Appel à l'API /chat avec streaming
        reply = ""
        try:
            resp = requests.post(HAILO_URL, json=payload, stream=True, timeout=180)
            resp.raise_for_status()
            
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        # Format de l'API /chat : message.content
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            reply += chunk
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            print(f"[ERREUR HAILO] {e}")
            reply = ""
        
        # ✅ Nettoyage anti-hallucination
        reply = strip_prompt_leakage(reply)
        
        # Nettoyage basique des markdown (optionnel)
        reply = reply.replace("*", "").replace("#", "").replace("_", "")
        
        if reply:
            print(f"[IA] : {reply}")
            # Sauvegarder l'échange dans le STM (avec le texte ORIGINAL, pas le contexte)
            conversation_history.append({'role': 'user', 'content': user_text})
            conversation_history.append({'role': 'assistant', 'content': reply})
            
            # Limiter la mémoire à court terme (20 messages = 10 échanges)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
        else:
            print("[CERVEAU] (Aucune réponse générée)")
        
        return reply

    except Exception as e:
        print(f"\n[ERREUR CERVEAU] Impossible de contacter Ollama : {e}")
        return "Désolé, j'ai rencontré un problème cognitif."


def summarize_and_sleep():
    """
    Appelé quand l'agent part dormir.
    Prend tout le STM, demande un résumé à Ollama, et le sauvegarde dans le LTM.
    
    ✅ Mise à jour pour utiliser l'API /chat
    """
    global conversation_history
    if not conversation_history:
        return

    print("\n[CERVEAU] Sauvegarde des souvenirs en cours (LTM)...")

    # On rassemble la discussion
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    prompt = f"""Voici la transcription de notre dernière conversation :
{history_text}

Agis comme un observateur. Fais un résumé TRÈS BREF (1-2 phrases) des faits importants concernant PUREMENT l'utilisateur (son nom, ses goûts, ses projets). S'il n'y a rien d'important, réponds juste 'Rien de particulier'."""
    
    # ✅ Format JSON structuré pour l'API /chat
    messages = [
        {'role': 'system', 'content': 'Tu es un synthétiseur de mémoire très factuel.'},
        {'role': 'user', 'content': prompt}
    ]
    
    payload = {
        "model": TEXT_MODEL,
        "messages": messages,
        "stream": True
    }

    try:
        reply_summary = ""
        resp = requests.post(HAILO_URL, json=payload, stream=True, timeout=60)
        resp.raise_for_status()
        
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        reply_summary += chunk
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    pass

        summary = strip_prompt_leakage(reply_summary).strip()

        # On évite de polluer la mémoire si rien ne s'est passé
        if summary and "Rien de particulier" not in summary:
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(summary + " ")
            print(f"[MÉMOIRE LTM] Nouveaux souvenirs sauvegardés : {summary}")
        else:
            print("[MÉMOIRE LTM] Rien d'important à mémoriser pour cette session.")

    except Exception as e:
        print(f"[ERREUR MÉMOIRE] Échec de la synthèse : {e}")

    # Vider la mémoire à court terme pour la prochaine session
    conversation_history = []


if __name__ == "__main__":
    print("\n--- TEST DU MODULE CERVEAU (LLM) ---")
    texte_test = "Bonjour, présente toi rapidement en une phrase courte s'il te plaît."
    reponse = think(texte_test)
    print(f"\nRésultat final retourné par la fonction : '{reponse}'")
