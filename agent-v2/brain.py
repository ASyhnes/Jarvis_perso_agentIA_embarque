from ollama import Client
import os

# Configuration du modèle et du client
TEXT_MODEL = "gemma3:1b"
SYSTEM_PROMPT = "Tu es un assistant vocal intelligent. Tu réponds TOUJOURS en français, de manière concise et naturelle. Tu n'utilises jamais de markdown, d'astérisques, de tirets ou de mise en forme. Tu réponds uniquement en texte brut."
ollama_client = Client(host='http://127.0.0.1:11434')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(PROJECT_ROOT, "long_term_memory.txt")

# Mémoire à court terme (STM) : stocke la conversation de la session courante
conversation_history = []

def get_long_term_memory():
    """Lit le fichier de mémoire à long terme s'il existe."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return f"Voici ce que tu as appris sur moi lors de nos précédentes discussions : {content}"
    return "Nous n'avons pas encore de souvenirs passés ensemble."

def think(user_text):
    """
    Prend le texte transcrit par Whisper et interroge l'IA (Ollama).
    Retourne la réponse textuelle complète de l'IA (pas de stream).
    """
    if not user_text.strip():
        return ""
        
    print(f"\n[CERVEAU] Réflexion sur : '{user_text}' ...")
    
    try:
        global conversation_history
        
        # System prompt de base (langue + style)
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        
        # Injection de la Mémoire à Long Terme seulement si elle existe
        ltm = get_long_term_memory()
        if "Voici ce que tu as appris" in ltm:
            messages.append({'role': 'system', 'content': f"Souvenir de tes échanges passés avec David : {ltm}"})
        
        # Ajout de la Mémoire à Court Terme (historique de la session)
        messages.extend(conversation_history)
        
        # Ajout de la nouvelle question
        messages.append({'role': 'user', 'content': user_text})
        
        # Appel à Ollama classique (bloquant jusqu'à la fin de la réponse) avec optimisations RPi
        response = ollama_client.chat(
            model=TEXT_MODEL, 
            messages=messages,
            keep_alive="1h",
            options={"num_ctx": 2048}
        )
        
        reply = response.get('message', {}).get('content', '')
        
        # Nettoyage
        reply = reply.replace("*", "").replace("#", "").replace("_", "")
        
        if reply:
            print(f"[IA] : {reply}")
            # Sauvegarder cet échange dans le STM
            conversation_history.append({'role': 'user', 'content': user_text})
            conversation_history.append({'role': 'assistant', 'content': reply})
            
            # Limiter la mémoire à court terme
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
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
    """
    global conversation_history
    if not conversation_history:
        return
        
    print("\n[CERVEAU] Sauvegarde des souvenirs en cours (LTM)...")
    
    # On rassemble la discussion pour Ollama
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    prompt = f"Voici la transcription de notre dernière conversation :\n{history_text}\n\nAgis comme un observateur. Fais un résumé TRÈS BREF (1-2 phrases) des faits importants concernant PUREMENT l'utilisateur (son nom, ses goûts, ses projets). S'il n'y a rien d'important, réponds juste 'Rien de particulier'."
    
    try:
        response = ollama_client.chat(model=TEXT_MODEL, messages=[
            {'role': 'system', 'content': "Tu es un synthétiseur de mémoire très factuel."},
            {'role': 'user', 'content': prompt}
        ])
        
        summary = response.get('message', {}).get('content', '').strip()
        
        # On évite de polluer la mémoire si rien ne s'est passé
        if summary and "Rien de particulier" not in summary:
            # On ajoute le résumé au fichier (ou on écrase, selon la strat. Pour l'instant on ajoute à la fin)
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(summary + " ")
            print(f"[MÉMOIRE LTM] Nouveaux souvenirs sauvegardés : {summary}")
        else:
            print("[MÉMOIRE LTM] Rien d'important à mémoriser pour cette session.")
            
    except Exception as e:
        print(f"[ERREUR MÉMOIRE] Échec de la synthèse : {e}")
        
    # Vider la mémoire à court terme pour la prochaine session !
    conversation_history = []

if __name__ == "__main__":
    print("\n--- TEST DU MODULE CERVEAU (LLM) ---")
    texte_test = "Bonjour, présente toi rapidement en une phrase courte s'il te plaît."
    reponse = think(texte_test)
    print(f"\nRésultat final retourné par la fonction : '{reponse}'")
