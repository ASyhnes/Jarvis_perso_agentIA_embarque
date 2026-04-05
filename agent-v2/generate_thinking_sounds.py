"""
Génère les fichiers WAV des phrases de patience avec Piper.
À lancer une seule fois : python generate_thinking_sounds.py
"""

import subprocess
import os
import struct

PIPER_BINARY = os.path.expanduser("~/piper_bin/piper")
VOICE_MODEL  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "piper/fr_FR-upmc-medium.onnx")
OUTPUT_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thinking_sounds")

PHRASES = [
    "oui?",
    "ok",
    "deux minutes, je réfléchis",
    "hum... vaste question"
]

def raw_to_wav(raw_bytes: bytes, sample_rate: int = 22050, channels: int = 1, bits: int = 16) -> bytes:
    """Encapsule des bytes PCM bruts dans un en-tête WAV standard."""
    data_size = len(raw_bytes)
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE',
        b'fmt ', 16, 1, channels,
        sample_rate, sample_rate * channels * bits // 8,
        channels * bits // 8, bits,
        b'data', data_size
    )
    return header + raw_bytes


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(PIPER_BINARY):
        print(f"[ERREUR] Piper introuvable : {PIPER_BINARY}")
        return
    if not os.path.exists(VOICE_MODEL):
        print(f"[ERREUR] Modèle voix introuvable : {VOICE_MODEL}")
        return

    print(f"Génération de {len(PHRASES)} fichiers dans '{OUTPUT_DIR}' ...\n")

    for i, phrase in enumerate(PHRASES):
        filename = os.path.join(OUTPUT_DIR, f"thinking_{i:02d}.wav")
        print(f"  [{i+1:02d}] {phrase}")

        proc = subprocess.Popen(
            [PIPER_BINARY, "--model", VOICE_MODEL, "--output-raw"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        raw_audio, _ = proc.communicate(input=phrase.encode("utf-8"))
        wav_bytes = raw_to_wav(raw_audio)

        with open(filename, "wb") as f:
            f.write(wav_bytes)
        print(f"       → {filename} ({len(wav_bytes)} bytes)")

    print(f"\n✅ Terminé ! {len(PHRASES)} fichiers générés.")


if __name__ == "__main__":
    main()
