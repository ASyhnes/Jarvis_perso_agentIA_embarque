"""
Benchmark de performance — Agent V2
=====================================
Mesure le temps de chaque étape : STT (Whisper), LLM (Ollama), TTS (Piper)
et génère un rapport lisible dans le terminal + un fichier benchmark_report.txt.

Usage:
    python agent-v2/benchmark.py
"""

import sys
import os
import time
import wave
import struct
import subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Configuration ────────────────────────────────────────────────────────────
TEST_PHRASES = [
    "Bonjour, comment vas-tu ?",
    "Quelle est la capitale de la France ?",
    "Explique-moi ce qu'est l'intelligence artificielle en une phrase.",
]

PIPER_BINARY = os.path.expanduser("~/piper_bin/piper")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_MODEL  = os.path.join(PROJECT_ROOT, "piper/fr_FR-siwis-low.onnx")
TEST_AUDIO   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests-micro", "input.wav")
REPORT_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_report.txt")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def sec(t): return f"{t:.2f}s"

def bar(value, max_val=10, width=20):
    """Barre de progression ASCII."""
    filled = int((value / max_val) * width)
    filled = min(filled, width)
    return f"[{'█' * filled}{'░' * (width - filled)}]"

def generate_test_wav(output_path, duration=2, sample_rate=16000):
    """Génère un fichier WAV de silence pour tester Whisper sans micro."""
    samples = np.zeros(int(duration * sample_rate), dtype=np.int16)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())

# ─── Tests individuels ────────────────────────────────────────────────────────
def bench_whisper(wav_path):
    """Mesure le temps de transcription Whisper."""
    if not os.path.exists(wav_path):
        generate_test_wav(wav_path)
    from whisper import transcribe_audio
    t0 = time.time()
    result = transcribe_audio(wav_path)
    return time.time() - t0, result or "(silence/rien détecté)"

def bench_llm(phrase, client, model):
    """Mesure le temps de réponse du LLM pour une phrase donnée."""
    t0 = time.time()
    response = client.chat(model=model, messages=[
        {'role': 'system', 'content': "Réponds en français, en une phrase courte maximum."},
        {'role': 'user', 'content': phrase}
    ])
    elapsed = time.time() - t0
    reply = response.get('message', {}).get('content', '').strip()
    return elapsed, reply

def bench_tts(text):
    """Mesure le temps de génération audio Piper (sans lecture)."""
    if not os.path.exists(PIPER_BINARY) or not os.path.exists(VOICE_MODEL):
        return None, "Piper ou modèle introuvable"
    t0 = time.time()
    proc = subprocess.Popen(
        [PIPER_BINARY, "--model", VOICE_MODEL, "--output-raw"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    stdout, _ = proc.communicate(input=text.encode('utf-8'))
    elapsed = time.time() - t0
    audio_kb = len(stdout) / 1024
    return elapsed, f"{audio_kb:.0f} KB audio générés"

# ─── Rapport ──────────────────────────────────────────────────────────────────
def print_separator(char="─", width=60):
    print(char * width)

def format_row(label, value, note=""):
    note_str = f"  ({note})" if note else ""
    return f"  {label:<30} {value}{note_str}"

def main():
    from ollama import Client
    TEXT_MODEL = "gemma3:1b"
    ollama_client = Client(host='http://127.0.0.1:11434')

    lines = []  # Pour le fichier rapport
    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("=" * 60)
    log("  BENCHMARK PERFORMANCE — AGENT V2")
    log(f"  Modèle LLM : {TEXT_MODEL}")
    log(f"  Date       : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    # ── 1. WHISPER ─────────────────────────────────────────────
    log()
    log("┌─ ÉTAPE 1 : WHISPER (Speech-to-Text)")
    log("│  Transcription d'un fichier WAV de 2 secondes...")
    w_time, w_result = bench_whisper(TEST_AUDIO)
    log(f"│  Résultat : '{w_result}'")
    log(f"│  ⏱  Durée : {sec(w_time)}  {bar(w_time, max_val=15)}")
    if w_time < 3:
        log("│  ✅ Whisper est RAPIDE")
    elif w_time < 8:
        log("│  🟡 Whisper est MOYEN (normal sur RPi)")
    else:
        log("│  🔴 Whisper est LENT — vérifier le modèle utilisé")
    log("└" + "─" * 59)

    # ── 2. LLM ─────────────────────────────────────────────────
    log()
    log("┌─ ÉTAPE 2 : LLM OLLAMA (Gemma 3 1B)")

    llm_times = []
    # Test 1 : premier appel (modèle potentiellement à charger)
    log("│  [1/3] Premier appel (chargement modèle possible)...")
    t, r = bench_llm(TEST_PHRASES[0], ollama_client, TEXT_MODEL)
    llm_times.append(t)
    log(f"│       Q: {TEST_PHRASES[0]}")
    log(f"│       R: {r[:60]}...")
    log(f"│       ⏱  {sec(t)}  {bar(t, max_val=20)}")

    # Tests suivants (modèle déjà en RAM)
    for i, phrase in enumerate(TEST_PHRASES[1:], 2):
        log(f"│  [{i}/3] Appel avec modèle chaud...")
        t, r = bench_llm(phrase, ollama_client, TEXT_MODEL)
        llm_times.append(t)
        log(f"│       Q: {phrase}")
        log(f"│       R: {r[:60]}")
        log(f"│       ⏱  {sec(t)}  {bar(t, max_val=20)}")

    llm_cold = llm_times[0]
    llm_warm = sum(llm_times[1:]) / len(llm_times[1:]) if len(llm_times) > 1 else llm_times[0]
    log(f"│")
    log(f"│  📊 Temps modèle FROID (1er appel)  : {sec(llm_cold)}")
    log(f"│  📊 Temps modèle CHAUD (moy.)       : {sec(llm_warm)}")
    log(f"│  📊 Surcoût du chargement            : +{sec(llm_cold - llm_warm)}")
    if llm_cold - llm_warm > 3:
        log("│  ⚠️  ATTENTION : le surcoût de chargement est élevé !")
        log("│     → Le modèle est déchargé entre chaque session.")
        log("│     → Solution : garder Ollama actif (keep_alive).")
    log("└" + "─" * 59)

    # ── 3. TTS PIPER ───────────────────────────────────────────
    log()
    log("┌─ ÉTAPE 3 : TTS PIPER (Text-to-Speech)")
    test_text = "Bonjour, je suis votre assistant vocal. Comment puis-je vous aider ?"
    log(f"│  Texte test : '{test_text}'")
    p_time, p_info = bench_tts(test_text)
    if p_time is not None:
        log(f"│  {p_info}")
        log(f"│  ⏱  Durée : {sec(p_time)}  {bar(p_time, max_val=5)}")
        if p_time < 1:
            log("│  ✅ Piper est RAPIDE")
        elif p_time < 2:
            log("│  🟡 Piper est MOYEN")
        else:
            log("│  🔴 Piper est LENT")
    else:
        log(f"│  ❌ {p_info}")
    log("└" + "─" * 59)

    # ── SYNTHÈSE ───────────────────────────────────────────────
    log()
    log("=" * 60)
    log("  SYNTHÈSE — TEMPS TOTAL (estimation par échange)")
    log("=" * 60)
    total_cold = w_time + llm_cold + (p_time or 0)
    total_warm = w_time + llm_warm + (p_time or 0)
    log(f"  Whisper (STT)           : {sec(w_time)}")
    log(f"  LLM 1er appel (froid)   : {sec(llm_cold)}")
    log(f"  LLM appels suivants     : {sec(llm_warm)}")
    log(f"  TTS Piper               : {sec(p_time or 0)}")
    log(f"")
    log(f"  ⏱  TOTAL 1er échange    : ~{sec(total_cold)}")
    log(f"  ⏱  TOTAL échanges suivants : ~{sec(total_warm)}")
    log()
    log("  GOULOTS D'ÉTRANGLEMENT :")
    bottlenecks = sorted([
        ("Whisper", w_time),
        ("LLM (froid)", llm_cold),
        ("TTS Piper", p_time or 0),
    ], key=lambda x: x[1], reverse=True)
    for rank, (name, t) in enumerate(bottlenecks, 1):
        log(f"  #{rank} {name:<20} {sec(t)}")
    log("=" * 60)

    # Sauvegarde du rapport
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log()
    log(f"  📄 Rapport sauvegardé : {REPORT_FILE}")
    log()

if __name__ == "__main__":
    main()
