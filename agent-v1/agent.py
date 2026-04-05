import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import os
import subprocess
import wave
import sounddevice as sd
import numpy as np
import scipy.signal
from ollama import Client

# =========================================================================
# 1. RECHERCHE DYNAMIQUE DES INDEX AUDIO
# =========================================================================

def get_audio_indices():
    devices = sd.query_devices()
    mic_idx = None
    spk_idx = None
    
    print("\n--- SCAN DES PÉRIPHÉRIQUES AUDIO ---")
    for i, dev in enumerate(devices):
        # MICRO : On cherche le "Sound Device" (Card 2 dans arecord -l)
        if "USB PnP Sound Device" in dev['name'] and dev['max_input_channels'] > 0:
            mic_idx = i
            print(f"[SYSTEM] MICRO trouvé à l'index {i} : {dev['name']}")
            
        # ENCEINTE : On cherche le "Audio Device" (Card 3 dans aplay -l)
        if "USB PnP Audio Device" in dev['name'] and dev['max_output_channels'] > 0:
            spk_idx = i
            print(f"[SYSTEM] ENCEINTE trouvée à l'index {i} : {dev['name']}")
            
    return mic_idx, spk_idx

MIC_INDEX, SPK_INDEX = get_audio_indices()

# Paramètres techniques
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPER_BINARY = os.path.expanduser("~/piper_bin/piper")
VOICE_MODEL = os.path.join(PROJECT_ROOT, "voices/fr_FR-siwis-medium.onnx")
TEXT_MODEL = "llama3.2:1b"
WHISPER_BIN = os.path.join(PROJECT_ROOT, "whisper.cpp/build/bin/whisper-cli")
WHISPER_MODEL = os.path.join(PROJECT_ROOT, "whisper.cpp/models/ggml-base.bin") 

ollama_client = Client(host='http://127.0.0.1:11434')

class BotStates:
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    WARMUP = "warmup"

# =========================================================================
# 2. INTERFACE GRAPHIQUE
# =========================================================================

class BotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Jarvis-BMO")
        master.attributes('-fullscreen', True)
        self.current_state = BotStates.WARMUP
        self.animations = {}
        self.current_frame_index = 0
        
        self.background_label = tk.Label(master)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.load_animations()
        self.update_animation()
        
        threading.Thread(target=self.main_loop, daemon=True).start()

    def load_animations(self):
        for state in [BotStates.IDLE, BotStates.LISTENING, BotStates.THINKING, BotStates.SPEAKING, BotStates.WARMUP]:
            path = os.path.join(PROJECT_ROOT, f"faces/{state}")
            self.animations[state] = []
            if os.path.exists(path):
                files = sorted([f for f in os.listdir(path) if f.endswith(".png")])
                for f in files:
                    img = Image.open(os.path.join(path, f)).resize((800, 480))
                    self.animations[state].append(ImageTk.PhotoImage(img))
            if not self.animations[state]:
                img = Image.new('RGB', (800, 480), color='#77b5a1')
                self.animations[state].append(ImageTk.PhotoImage(img))

    def update_animation(self):
        frames = self.animations.get(self.current_state, [])
        if frames:
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)
            self.background_label.config(image=frames[self.current_frame_index])
        
        delay = 80 if self.current_state == BotStates.SPEAKING else 500
        self.master.after(delay, self.update_animation)

    def set_state(self, state):
        self.current_state = state

    # =========================================================================
    # 3. LOGIQUE IA ET AUDIO
    # =========================================================================

    def main_loop(self):
        print("\n--- JARVIS-BMO : SYSTÈME PRÊT ---")
        
        while True:
            self.set_state(BotStates.IDLE)
            print("\n[VUE] En attente de son...", end="\r")
            
            try:
                audio_file = self.record_audio()
                
                if audio_file:
                    self.set_state(BotStates.THINKING)
                    user_text = self.transcribe_audio(audio_file)
                    
                    if user_text and len(user_text) > 3:
                        if "[Musique]" in user_text or "[Audio]" in user_text:
                            continue

                        print(f"\n[ENTENDU] : \"{user_text}\"")
                        
                        response = ollama_client.chat(model=TEXT_MODEL, messages=[
                            {'role': 'user', 'content': user_text}
                        ])
                        reply = response['message']['content']
                        print(f"[JARVIS] : {reply}")
                        
                        self.set_state(BotStates.SPEAKING)
                        self.speak(reply)
                
                time.sleep(0.3) 

            except Exception as e:
                print(f"\n[ERREUR] : {e}")
                time.sleep(2)

    def record_audio(self, filename=None):
        if filename is None:
            filename = os.path.join(PROJECT_ROOT, "input.wav")
        duration = 4 
        if MIC_INDEX is None: return None

        try:
            info = sd.query_devices(MIC_INDEX, 'input')
            native_fs = int(info['default_samplerate'])
            channels = int(info['max_input_channels'])
            if channels > 2: channels = 2 
            
            rec = sd.rec(int(duration * native_fs), samplerate=native_fs, 
                         channels=channels, dtype='int16', device=MIC_INDEX)
            sd.wait()
            
            mono = rec[:, 0] if channels == 2 else rec.flatten()
            
            if np.max(np.abs(mono)) < 200:
                return None

            print("\n[CAPTURÉ] Son détecté...")
            self.set_state(BotStates.LISTENING)

            if native_fs != 16000:
                num_samples = int(len(mono) * 16000 / native_fs)
                mono = scipy.signal.resample(mono, num_samples).astype(np.int16)

            with wave.open(filename, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(mono.tobytes())
            return filename

        except Exception as e:
            print(f"\n[ERREUR AUDIO IN] : {e}")
            return None

    def transcribe_audio(self, filename):
        try:
            cmd = [WHISPER_BIN, "-m", WHISPER_MODEL, "-f", filename, "-l", "fr", "-nt"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return result.stdout.strip()
        except:
            return ""

    def speak(self, text):
        try:
            proc = subprocess.Popen(
                [PIPER_BINARY, "--model", VOICE_MODEL, "--output-raw"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            stdout, _ = proc.communicate(input=text.encode())
            audio_data = np.frombuffer(stdout, dtype=np.int16)
            
            # SORTIE SUR L'ENCEINTE (SPK_INDEX)
            sd.play(audio_data, 22050, device=SPK_INDEX)
            sd.wait()
        except Exception as e:
            print(f"\n[ERREUR VOIX OUT] : {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BotGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nArrêt.")