class BotStates:
    WARMUP = "warmup"
    SLEEP = "sleep"       # Agent dort, n'attend que le mot de réveil
    IDLE = "idle"         # Agent réveillé, attend qu'on lui parle
    LISTENING = "listening" # En train d'enregistrer la voix
    THINKING = "thinking" # En attente d'Ollama (LLM)
    SPEAKING = "speaking" # En train de jouer l'audio Piper

class StateManager:
    def __init__(self, ui_callback=None):
        """
        Gère l'état courant de l'agent.
        ui_callback: Fonction à appeler quand l'état change (pour mettre à jour le visage)
        """
        self._current_state = BotStates.WARMUP
        self._ui_callback = ui_callback
        
    @property
    def current(self):
        return self._current_state
        
    def set(self, new_state):
        if self._current_state != new_state:
            self._current_state = new_state
            # Si on a fourni une fonction pour l'UI, on met à jour l'image
            if self._ui_callback:
                self._ui_callback(new_state)
            
            # Affichage console pour le debug
            print(f"\n[ÉTAT] 🔄 Changement d'état : {new_state.upper()}")

# On peut ajouter ici plus tard la détection spécifique du mot de réveil (Wake Word)
# pour passer de l'état SLEEP à l'état IDLE.
