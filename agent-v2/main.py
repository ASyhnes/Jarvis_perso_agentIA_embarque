import tkinter as tk
import threading
import os
import time
import random
import re
import subprocess
import requests as _requests
import sounddevice as sd

from state import BotStates, StateManager
from micro import get_micro_index, listen_continuously
from speaker import get_speaker_index
from piper import speak
from brain import think, summarize_and_sleep
from wakeword import wait_for_wakeword, check_sleep_command
from visage import BotGUI

idle_timer = None

# Dossier contenant les phrases de patience pré-générées
THINKING_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thinking_sounds")

def get_alsa_output_device(sd_device_idx):
    """Extrait le nom ALSA (ex: 'plughw:3,0') depuis l'index sounddevice."""
    try:
        name = sd.query_devices(sd_device_idx)['name']
        match = re.search(r'hw:(\d+,\d+)', name)
        if match:
            return f"plughw:{match.group(1)}"
    except Exception:
        pass
    return None

def play_thinking_sound(device_idx=None):
    """
    Joue aléatoirement un fichier WAV de patience via aplay (ALSA).
    Évite les conflits avec le stream microphone sounddevice.
    """
    if not os.path.isdir(THINKING_SOUNDS_DIR):
        print(f"[PATIENCE] ⚠️  Dossier '{THINKING_SOUNDS_DIR}' introuvable. Lance generate_thinking_sounds.py d'abord.")
        return
    files = [f for f in os.listdir(THINKING_SOUNDS_DIR) if f.endswith(".wav")]
    if not files:
        return
    chosen = os.path.join(THINKING_SOUNDS_DIR, random.choice(files))
    print(f"[PATIENCE] 🔊 {os.path.basename(chosen)}")
    try:
        cmd = ["aplay"]
        alsa_dev = get_alsa_output_device(device_idx)
        if alsa_dev:
            cmd += ["-D", alsa_dev]
        cmd.append(chosen)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[PATIENCE] Erreur lecture : {e}")

def cleanup_ollama():
    """
    Demande à Ollama de décharger tous les modèles actuellement en RAM.
    On envoie keep_alive=0 pour chaque modèle chargé, ce qui force son éviction.
    """
    try:
        # Récupérer la liste des modèles actuellement chargés
        resp = _requests.get("http://127.0.0.1:11434/api/ps", timeout=5)
        if resp.status_code != 200:
            return
        loaded = resp.json().get("models", [])
        if not loaded:
            print("[INIT] Aucun modèle Ollama en RAM. C'est propre !")
            return
        
        print(f"[INIT] {len(loaded)} modèle(s) chargé(s) en RAM. Nettoyage...")
        for m in loaded:
            name = m.get("name", "")
            _requests.post("http://127.0.0.1:11434/api/generate",
                json={"model": name, "keep_alive": 0}, timeout=10)
            print(f"[INIT] Modèle '{name}' déchargé de la RAM.")
        print("[INIT] Nettoyage terminé. La RAM est disponible.")
        time.sleep(1) # Laisser le temps à Ollama de libérer

    except Exception as e:
        print(f"[INIT] Avertissement : impossible de nettoyer Ollama : {e}")

def start_agent_logic(state_manager):
    """
    S'exécute dans un thread séparé pour ne pas bloquer l'interface Tkinter.
    """
    # 1. On laisse le temps à l'UI de démarrer et afficher le WARMUP
    time.sleep(2)
    
    # 1.5 On libère tous les modèles Ollama en RAM avant de charger le nôtre
    cleanup_ollama()
    
    # 2. Détection du matériel audio
    mic_idx = get_micro_index()
    spk_idx = get_speaker_index()
    
    if mic_idx is None or spk_idx is None:
        print("[AVERTISSEMENT] Il manque le micro ou l'enceinte. L'Agent V2 démarre tout de même en mode visuel (dégradé).")
        # On ne fait pas return ici, pour que l'interface puisse quand même s'animer (pour le test).
        
    def handle_voice_input(transcription):
        """Callback appelé par micro.py dès qu'une phrase a été identifiée et traduite !"""
        global idle_timer
        
        if idle_timer and idle_timer.is_alive():
            idle_timer.cancel()
            
        if not transcription:
            return
            
        print(f"\n[MAIN] Whisper a entendu : {transcription}")
        
        # --- LOGIQUE DE RÉVEIL TEXTUEL ---
        if state_manager.current == BotStates.SLEEP:
            wait_for_wakeword(transcription, state_manager, spk_idx)
            return

        # Si on est déjà réveillé, on vérifie d'abord si on doit se rendormir
        is_sleeping = check_sleep_command(transcription, state_manager, spk_idx)
        if is_sleeping:
            return

        # --- LOGIQUE D'ACTION NORMALE (Quand l'agent est réveillé) ---
        # 1. Phrase de patience pendant que le LLM réfléchit
        state_manager.set(BotStates.THINKING)
        patience_thread = threading.Thread(
            target=play_thinking_sound, args=(spk_idx,), daemon=True
        )
        patience_thread.start()
        
        # 2. Réflexion du Cerveau ! (Ollama LLM) — en parallèle du son
        t_llm_start = time.time()
        reply = think(transcription)
        t_llm_end = time.time()
        print(f"⏱️  [TEMPS] Cerveau sollicité en {t_llm_end - t_llm_start:.2f}s")
        
        # Attendre que la phrase de patience soit finie avant d'ouvrir le canal de la vraie voix
        patience_thread.join()
        
        # 3. Synthèse vocale de la réponse (Piper)
        if reply:
            t_tts_start = time.time()
            speak(reply, device_idx=spk_idx, state_manager=state_manager)
            t_tts_end = time.time()
            print(f"⏱️  [TEMPS] Échange vocal terminé en {t_tts_end - t_tts_start:.2f}s")
            
        # 3. Fin de parole, on reste attentif (LISTENING) pendant 20 secondes
        state_manager.set(BotStates.LISTENING)
        
        def reset_to_idle():
            if state_manager.current == BotStates.LISTENING:
                
                # On passe en SLEEP IMMÉDIATEMENT pour que le prochain mot
                # déclenche bien le mot de réveil, comme au démarrage.
                print("\n[ÉTAT] 🔄 Expiration du délai actif. Retour en veille...")
                state_manager.set(BotStates.SLEEP)
                print("[ÉCOUTE] En attente du mot de réveil...")
                
                # La synthèse mémoire tourne en arrière-plan sans bloquer
                threading.Thread(target=summarize_and_sleep, daemon=True).start()
                
        idle_timer = threading.Timer(20.0, reset_to_idle)
        idle_timer.start()
        
    print("\n--- JARVIS-BMO V2 : LANCEMENT DE L'ÉCOUTE ---")
    state_manager.set(BotStates.SLEEP)
    
    # La fonction écoute en boucle bloquante. 
    # Elle s'occupera d'appeler le "handle_voice_input" quand il y a du texte !
    listen_continuously(
        device_idx=mic_idx, 
        threshold=450, 
        on_transcription=handle_voice_input, 
        state_manager=state_manager
    )

if __name__ == "__main__":
    # Début du programme, création du gestionnaire d'état partagé entre les threads
    state_mgr = StateManager()
    state_mgr.set(BotStates.WARMUP)
    
    # Lancement de la logique (Micro/IA/Voix) en arrière-plan
    logic_thread = threading.Thread(target=start_agent_logic, args=(state_mgr,), daemon=True)
    logic_thread.start()
    
    # Lancement de l'interface graphique principale !
    try:
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0"  # X11 fallback
        if "WAYLAND_DISPLAY" not in os.environ:
            os.environ["WAYLAND_DISPLAY"] = "wayland-1" # Wayland primaire (Raspberry Pi Bookworm)
        if "XDG_RUNTIME_DIR" not in os.environ:
            os.environ["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
            
        root = tk.Tk()
        app = BotGUI(root, state_mgr)
        root.mainloop()
    except tk.TclError as e:
        print(f"\n[INFO] Interface graphique non disponible ({e}).")
        print("[INFO] L'agent tourne maintenant en mode 'Console' (headless).\n")
        try:
            # Boucle infinie pour garder le thread principal en vie
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nArrêt du programme principal.")
    except KeyboardInterrupt:
        print("\nArrêt du programme principal.")
