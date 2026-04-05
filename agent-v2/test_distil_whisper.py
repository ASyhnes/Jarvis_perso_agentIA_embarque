"""
Test distil-whisper/distil-large-v3-fr via faster-whisper
-----------------------------------------------------------
Premier lancement : télécharge le modèle (~1.5GB) depuis Hugging Face.
Lancements suivants : utilise le cache local.

Usage:
    python agent-v2/test_distil_whisper.py
"""

import sys
import os
import time
import wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TEST_AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "tests-micro", "input.wav")

# ─── Génération d'un WAV de test si nécessaire ──────────────────────────────
def ensure_test_wav(path):
    if not os.path.exists(path):
        print("[INFO] Génération d'un WAV de silence pour le test...")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        samples = np.zeros(int(2 * 16000), dtype=np.int16)
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(samples.tobytes())


def main():
    from faster_whisper import WhisperModel

    print("=" * 60)
    print("  TEST — distil-whisper/distil-large-v3-fr")
    print("=" * 60)
    print()
    print("⏳ Chargement du modèle (téléchargement si premier lancement)...")
    print("   Taille : ~1.5 GB — patience 🙏")
    print()

    t_load = time.time()
    model = WhisperModel(
        "Systran/faster-distil-whisper-large-v3",  # version CTranslate2 (compatible faster-whisper)
        device="cpu",
        compute_type="int8",               # quantisation int8 pour le RPi
        # cpu_threads=4,                   # décommenter si tu veux limiter les cœurs
    )
    load_time = time.time() - t_load
    print(f"✅ Modèle chargé en {load_time:.1f}s")
    print()

    ensure_test_wav(TEST_AUDIO)

    # ─── Transcription ────────────────────────────────────────────────────────
    print(f"🎤 Transcription de : {TEST_AUDIO}")
    t_stt = time.time()
    segments, info = model.transcribe(
        TEST_AUDIO,
        language="fr",
        beam_size=1,          # beam_size=1 = greedy, plus rapide
        vad_filter=True,      # filtre le silence automatiquement
    )
    text = " ".join(seg.text.strip() for seg in segments)
    stt_time = time.time() - t_stt

    print()
    print("─" * 60)
    print(f"  Résultat    : '{text or '(silence détecté)'}'")
    print(f"  ⏱  Durée STT : {stt_time:.2f}s")
    print(f"  🌍 Langue    : {info.language} (confiance {info.language_probability:.0%})")
    print("─" * 60)
    print()

    # ─── Comparatif ──────────────────────────────────────────────────────────
    print("📊 COMPARATIF vs whisper.cpp base :")
    print(f"   whisper.cpp base    : ~2.6s")
    print(f"   distil-large-v3-fr : {stt_time:.2f}s  ({'+' if stt_time > 2.6 else ''}{stt_time - 2.6:.1f}s)")
    print()
    if stt_time < 2.6:
        print("  ✅ distil-whisper est PLUS RAPIDE → migration recommandée")
    else:
        print("  🟡 distil-whisper est plus lent sur ce RPi → garder whisper.cpp base")
    print()


if __name__ == "__main__":
    main()
