import tkinter as tk
from PIL import Image, ImageTk
import os
from state import BotStates

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class BotGUI:
    def __init__(self, master, state_manager):
        self.master = master
        self.state_manager = state_manager
        
        master.title("Jarvis-BMO V2")
        master.attributes('-fullscreen', True)
        
        self.animations = {}
        self.current_frame_index = 0
        
        self.background_label = tk.Label(master)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.load_animations()
        self.update_animation()

    def load_animations(self):
        """Charger toutes les animations depuis le dossier faces."""
        for state in [BotStates.SLEEP, BotStates.IDLE, BotStates.LISTENING, BotStates.THINKING, BotStates.SPEAKING, BotStates.WARMUP]:
            path = os.path.join(PROJECT_ROOT, f"faces/{state}")
            self.animations[state] = []
            if os.path.exists(path):
                files = sorted([f for f in os.listdir(path) if f.endswith(".png")])
                for f in files:
                    img = Image.open(os.path.join(path, f)).resize((800, 480))
                    self.animations[state].append(ImageTk.PhotoImage(img))
            
            # Si aucune image n'est trouvée pour cet état, on génère un fond uni de couleur (vert d'eau BMO)
            if not self.animations[state]:
                img = Image.new('RGB', (800, 480), color='#77b5a1')
                self.animations[state].append(ImageTk.PhotoImage(img))

    def update_animation(self):
        """Lit l'état actuel et met à jour l'image à l'écran en boucle."""
        current_state = self.state_manager.current
        frames = self.animations.get(current_state, [])
        if frames:
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)
            self.background_label.config(image=frames[self.current_frame_index])
        
        # Vitesse de l'animation, plus rapide quand l'agent parle
        delay = 80 if current_state == BotStates.SPEAKING else 500
        self.master.after(delay, self.update_animation)
