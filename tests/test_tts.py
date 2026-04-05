import sounddevice as sd
import numpy as np
import subprocess
import wave
import scipy.signal
import sys
import os

def test_tts(text="Bonjour ! Je suis Jarvis, et c'est un test de ma sortie vocale."):
    print("Recherche de tous les périphériques audio sortants...")
    devices = sd.query_devices()
    
    output_device = None
    for i, dev in enumerate(devices):
        if dev['max_output_channels'] > 0 and ('USB' in dev['name'] or 'Audio' in dev['name']):
            output_device = dev['name']
            print(f"✅ Enceinte trouvée : {dev['name']}")
            break
            
    if not output_device:
        print("❌ Aucune enceinte USB trouvée.")
        return

    print(f"🧠 Piper génère l'audio pour : '{text}'...")
    try:
        piper_cmd = [
            "./piper/piper",
            "--model", "piper/fr_FR-upmc-medium.onnx",
            "--output_file", "test_tts.wav"
        ]
        process = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=text.encode("utf-8"))
    except Exception as e:
        print(f"❌ Erreur de génération Piper: {e}")
        return

    if not os.path.exists("test_tts.wav"):
         print("❌ Erreur: Le fichier test_tts.wav n'a pas été créé par Piper.")
         return

    print(f"🔊 Lecture de l'audio généré sur {output_device}...")
    try:
        with wave.open("test_tts.wav", 'rb') as wf:
            file_sr = wf.getframerate()
            data = wf.readframes(wf.getnframes())
            audio = np.frombuffer(data, dtype=np.int16)

        # Resampling logiciel forcé pour les enceintes qui ne supportent pas le sample rate de base de Piper (22050Hz)
        playback_rate = 44100
        num_samples = int(len(audio) * (playback_rate / file_sr))
        audio = scipy.signal.resample(audio, num_samples).astype(np.int16)

        sd.play(audio, playback_rate, device=output_device)
        sd.wait()
        print("✅ Terminé !")
    except Exception as e:
        print(f"❌ Erreur lecture audio: {e}")

if __name__ == "__main__":
    user_text = sys.argv[1] if len(sys.argv) > 1 else "Bonjour ! Je suis Jarvis, l'assistant vocal en python. Entendez-vous ma douce voix ?"
    test_tts(user_text)
