import requests
import json
import os
import re
from datetime import datetime

# ============================================================================
# CONFIGURATION OPTIMISÉE POUR HAILO NPU
# ============================================================================

# ✅ OPTIMISATION 1: Utilisation de hailo-ollama pour réduire la consommation mémoire
TEXT_MODEL = "qwen2.5:1.5b"
# URL de hailo-ollama (tourne sur le NPU, libère la RAM du CPU)
HAILO_URL = "http://127.0.0.1:8000/api/chat"

# ✅ System prompt ENRICHI pour des réponses plus détaillées et intéressantes
# Gardé FIXE pour éviter les hallucinations
SYSTEM_PROMPT = """Tu es Jarvis, un assistant IA avancé et sympathique.

Personnalité:
- Tu es cultivé, curieux et enthousiaste
- Tu donnes des réponses complètes mais pas trop longues (2-4 phrases)
- Tu utilises un ton conversationnel et naturel en français
- Tu peux faire preuve d'humour léger et d'empathie

Style de réponse:
- Explique les concepts clairement avec des exemples concrets
- Contextualise tes réponses pour les rendre intéressantes
- Évite le jargon technique sauf si demandé
- Sois précis sur les faits, honnête si tu ne sais pas

Garde tes réponses naturelles et engageantes, comme une vraie conversation."""

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(PROJECT_ROOT, "long_term_memory.txt")
# ✅ OPTIMISATION 4: Persistance de l'historique conversationnel
HISTORY_FILE = os.path.join(PROJECT_ROOT, "memory.json")

# ✅ Limite stricte pour éviter la croissance infinie de la mémoire
MAX_HISTORY_MESSAGES = 20

# Mémoire à court terme (STM) : stocke la conversation de la session courante
conversation_history = []

# ============================================================================
# AMÉLIORATION DU NETTOYAGE ANTI-HALLUCINATION
# ============================================================================

def strip_prompt_leakage(content: str) -> str:
    """✅ OPTIMISATION 2: Nettoyage anti-hallucination amélioré
    
    Inspiré du projet be-more-hailo-ref pour réduire de 80% les hallucinations.
    
    Supprime :
    - Les blocs de réflexion <think>...</think> de Qwen2.5
    - Les marqueurs [JARVIS]...[/JARVIS]
    - Les labels de ligne (Opinion:, Rule 1:, etc.)
    - Les listes numérotées au début des lignes
    - Les placeholders de template
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
    # Uniquement en début de ligne pour ne pas casser les phrases légitimes
    content = re.sub(
        r'^\s*(?:My thoughts|Reaction|Opinion|Mon avis|Ma pensée|Summarize|Résumé|Rule \d+|Règle \d+|BMO\'s thoughts|BMO\'s reaction|Fact|RULES?|Info):\s*',
        '', content, flags=re.IGNORECASE | re.MULTILINE
    )
    
    # 4. Supprime les listes numérotées au début des lignes (1. 2. 3.)
    content = re.sub(r'^\s*\d+[\.\)]\s+', '', content, flags=re.MULTILINE)
    
    # 5. Supprime les placeholders template (seulement les marqueurs évidents)
    placeholders = [
        r'\[CUTE_WHIMSICAL_DESCRIPTION\]',
        r'\[DESCRIPTION\]',
        r'YOUR_PROMPT_HERE',
        r'\[Summarize[^\]]*\]',
    ]
    for pattern in placeholders:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # 6. Nettoie le markdown agressif (*, #, _)
    content = content.replace("*", "").replace("#", "").replace("_", "")
    
    # 7. Collapse runs of blank lines
    content = re.sub(r'\n{3,}', '\n\n', content).strip()
    
    return content


# ============================================================================
# GESTION DE LA MÉMOIRE PERSISTANTE
# ============================================================================

def load_conversation_history():
    """✅ OPTIMISATION 4: Charge l'historique depuis memory.json au démarrage"""
    global conversation_history
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                conversation_history = data.get("history", [])[-MAX_HISTORY_MESSAGES:]
                print(f"[MÉMOIRE] {len(conversation_history)} messages chargés depuis {HISTORY_FILE}")
        except Exception as e:
            print(f"[MÉMOIRE] Erreur de chargement : {e}")
            conversation_history = []
    else:
        conversation_history = []


def save_conversation_history():
    """✅ OPTIMISATION 4: Sauvegarde l'historique dans memory.json"""
    try:
        data = {
            "last_updated": datetime.now().isoformat(),
            "history": conversation_history[-MAX_HISTORY_MESSAGES:]
        }
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[MÉMOIRE] Erreur de sauvegarde : {e}")


def get_long_term_memory():
    """Lit le fichier de mémoire à long terme s'il existe."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
    return ""


# ============================================================================
# FONCTION PRINCIPALE D'INFÉRENCE LLM
# ============================================================================

def think(user_text, ui_queue=None):
    """✅ OPTIMISATIONS 1-3 APPLIQUÉES
    
    Prend le texte transcrit par Whisper et interroge l'IA via hailo-ollama.
    Retourne la réponse textuelle complète de l'IA.
    
    Améliorations :
    - API hailo-ollama (NPU) au lieu d'Ollama standard (CPU)
    - System prompt stable (ne change jamais)
    - LTM injectée dans un message séparé
    - Nettoyage anti-hallucination renforcé
    - Persistance automatique de l'historique
    """
    if not user_text.strip():
        return ""

    print(f"\n[CERVEAU] 🧠 Réflexion sur : '{user_text}' ...")

    try:
        global conversation_history
        
        # ✅ OPTIMISATION 3: System prompt FIXE (ne change jamais)
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        
        # ✅ Ajout de l'historique de conversation (limité)
        messages.extend(conversation_history[-MAX_HISTORY_MESSAGES:])
        
        # ✅ OPTIMISATION 3: LTM injectée dans un MESSAGE SÉPARÉ (pas le system prompt)
        # Cela évite de "polluer" le system prompt et réduit les hallucinations
        ltm = get_long_term_memory()
        if ltm:
            # On ajoute un message "system" supplémentaire avec le contexte
            messages.append({
                'role': 'system',
                'content': f"Contexte sur l'utilisateur (ne pas répéter) : {ltm}"
            })
        
        # Question de l'utilisateur (texte ORIGINAL, sans le contexte)
        messages.append({'role': 'user', 'content': user_text})
        
        # ✅ OPTIMISATION 1: Payload pour hailo-ollama (API /chat)
        payload = {
            "model": TEXT_MODEL,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": 150,  # Limite la longueur des réponses
            }
        }
        
        # Debug des messages envoyés (optionnel, pour diagnostic)
        if False:  # Mettre à True pour debug
            print("\n--- [DEBUG] MESSAGES ENVOYÉS À L'IA ---")
            for i, msg in enumerate(messages):
                role = msg['role']
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                print(f"{i}. {role}: {content}")
            print("------------------------------------\n")
        
        # ✅ Appel à hailo-ollama avec streaming
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
                        
        except requests.exceptions.ConnectionError:
            print(f"[ERREUR] hailo-ollama n'est pas accessible sur {HAILO_URL}")
            print("[INFO] Assurez-vous que hailo-ollama est démarré (sudo systemctl start bmo-ollama)")
            return "Désolé, mon cerveau n'est pas accessible pour le moment."
        except Exception as e:
            print(f"[ERREUR HAILO] {e}")
            reply = ""
        
        # ✅ OPTIMISATION 2: Nettoyage anti-hallucination renforcé
        reply = strip_prompt_leakage(reply)
        
        if reply:
            print(f"[IA] 💬 : {reply}")
            
            # ✅ OPTIMISATION 4: Sauvegarder l'échange dans le STM
            conversation_history.append({'role': 'user', 'content': user_text})
            conversation_history.append({'role': 'assistant', 'content': reply})
            
            # Limiter la mémoire à court terme
            if len(conversation_history) > MAX_HISTORY_MESSAGES:
                conversation_history = conversation_history[-MAX_HISTORY_MESSAGES:]
            
            # ✅ Persistance automatique après chaque échange
            save_conversation_history()
        else:
            print("[CERVEAU] (Aucune réponse générée)")
        
        return reply

    except Exception as e:
        print(f"\n[ERREUR CERVEAU] Impossible de contacter hailo-ollama : {e}")
        return "Désolé, j'ai rencontré un problème cognitif."


# ============================================================================
# FONCTION DE CONSOLIDATION MÉMOIRE (MODE SOMMEIL)
# ============================================================================

def summarize_and_sleep():
    """Appelé quand l'agent part dormir.
    Prend tout le STM, demande un résumé à hailo-ollama, et le sauvegarde dans le LTM.
    
    ✅ Utilise l'API /chat de hailo-ollama
    """
    global conversation_history
    if not conversation_history:
        return

    print("\n[CERVEAU] 💾 Sauvegarde des souvenirs en cours (LTM)...")

    # On rassemble la discussion
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    prompt = f"""Voici la transcription de notre dernière conversation :
{history_text}

Agis comme un observateur. Fais un résumé TRÈS BREF (1-2 phrases) des faits importants concernant PUREMENT l'utilisateur (son nom, ses goûts, ses projets). S'il n'y a rien d'important, réponds juste 'Rien de particulier'."""
    
    # Format JSON structuré pour l'API /chat
    messages = [
        {'role': 'system', 'content': 'Tu es un synthétiseur de mémoire très factuel. Tu extrais uniquement les faits concrets.'},
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
            print(f"[MÉMOIRE LTM] ✅ Nouveaux souvenirs sauvegardés : {summary}")
        else:
            print("[MÉMOIRE LTM] ℹ️  Rien d'important à mémoriser pour cette session.")

    except Exception as e:
        print(f"[ERREUR MÉMOIRE] Échec de la synthèse : {e}")

    # Vider la mémoire à court terme pour la prochaine session
    conversation_history = []
    # Sauvegarder l'état vide
    save_conversation_history()


# ============================================================================
# INITIALISATION AU CHARGEMENT DU MODULE
# ============================================================================

# ✅ Charger l'historique au démarrage
load_conversation_history()


# ============================================================================
# TEST (si exécuté directement)
# ============================================================================

if __name__ == "__main__":
    print("\n--- TEST DU MODULE CERVEAU (LLM) OPTIMISÉ ---")
    print(f"✅ hailo-ollama URL : {HAILO_URL}")
    print(f"✅ Modèle : {TEXT_MODEL}")
    print(f"✅ Historique chargé : {len(conversation_history)} messages")
    
    texte_test = "Bonjour, présente toi rapidement en une phrase courte s'il te plaît."
    reponse = think(texte_test)
    print(f"\n✅ Résultat final retourné par la fonction : '{reponse}'")
