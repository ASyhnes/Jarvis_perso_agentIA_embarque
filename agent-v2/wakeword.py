from state import BotStates
from piper import speak

def wait_for_wakeword(transcription, state_manager, spk_idx):
    """
    Analyse le texte pour voir s'il contient le mot de réveil.
    Retourne True si l'agent se réveille, False s'il continue de dormir.
    """
    text_lower = transcription.lower()
    
    # Mots clés déclencheurs
    trigger_words = ["debout là dedans", "debout la dedans", "debout là-dedans", "debout la-dedans","javis", "jarvis", "bimo", "bimo", "bimo", "bimo", "bimo", "bimo", "debout", "alexa"]
    if any(w in text_lower for w in trigger_words):
        print("[WAKEWORD] 🔔 Mot de réveil reconnu !! L'agent se réveille.")
        speak("Oui, je t'écoute ?", device_idx=spk_idx, state_manager=state_manager)
        
        if state_manager:
            state_manager.set(BotStates.LISTENING)
        return True
    else:
        print("[WAKEWORD] 💤 L'agent dort, il ignore cette phrase.")
        return False

def check_sleep_command(transcription, state_manager, spk_idx):
    """
    Analyse le texte pour voir s'il contient une commande de mise en veille.
    Retourne True si l'agent s'est endormi, False sinon.
    """
    text_lower = transcription.lower()
    
    # Mots clés de sommeil
    if "dors" in text_lower or "sommeil" in text_lower or "merci" in text_lower or "stop" in text_lower:
        print("[WAKEWORD] � Commande de sommeil reçue.")
        if state_manager:
            pass
        speak("D'accord, je me mets en veille.", device_idx=spk_idx, state_manager=state_manager)
        import threading
        from brain import summarize_and_sleep
        def sleep_and_save():
            summarize_and_sleep()
            if state_manager:
                state_manager.set(BotStates.SLEEP)
        threading.Thread(target=sleep_and_save, daemon=True).start()
        
        if state_manager:
            state_manager.set(BotStates.SLEEP)
        return True
        
    return False

if __name__ == "__main__":
    import sys
    from micro import get_micro_index, listen_continuously
    from speaker import get_speaker_index
    from state import StateManager
    
    print("\n--- DÉBUT DU TEST DU WAKEWORD TEXTUEL ---")
    mic_idx = get_micro_index()
    spk_idx = get_speaker_index()
    
    if mic_idx is None:
        print("[ERREUR] Micro introuvable.")
        sys.exit(1)
        
    # Initialisation de l'état "endormi"
    state_mgr = StateManager()
    state_mgr.set(BotStates.SLEEP)
    
    def on_test_transcription(transcription):
        """Fonction appelée chaque fois que tu dis une phrase."""
        if not transcription:
            return
            
        print(f"\n[TEXTE ENTENDU] : {transcription}")
        
        if state_mgr.current == BotStates.SLEEP:
            # On cherche à se réveiller
            wait_for_wakeword(transcription, state_mgr, spk_idx)
        else:
            # On cherche à s'endormir
            check_sleep_command(transcription, state_mgr, spk_idx)
            
    print("\n[INFO TEST] Dites votre mot clé (ex: 'debout là dedans') pour réveiller l'agent.")
    print("[INFO TEST] Dites ('dors', 'stop') pour le remettre en veille.")
    
    # Lancement de l'écoute continue
    listen_continuously(
        device_idx=mic_idx,
        threshold=450,
        on_transcription=on_test_transcription,
        state_manager=state_mgr
    )
