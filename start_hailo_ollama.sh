#!/bin/bash
# ============================================================================
# Script de démarrage de hailo-ollama pour Jarvis-BMO
# ============================================================================

echo "🚀 Démarrage de hailo-ollama pour Jarvis-BMO..."

# Vérifier que le NPU Hailo est détecté
if [ ! -e /dev/hailo0 ]; then
    echo "❌ ERREUR: Le NPU Hailo n'est pas détecté (/dev/hailo0 absent)"
    echo "   Vérifiez que le AI HAT est bien connecté et que les drivers sont installés"
    exit 1
fi

# Vérifier que hailo-ollama est installé
if ! command -v hailo-ollama &> /dev/null; then
    echo "❌ ERREUR: hailo-ollama n'est pas installé"
    echo "   Installez-le depuis : https://github.com/hailo-ai/hailo_model_zoo_genai"
    exit 1
fi

# Arrêter l'instance existante si elle tourne
pkill -f "hailo-ollama serve" 2>/dev/null
sleep 2

# Note: Le modèle sera téléchargé automatiquement au premier usage si nécessaire
echo "ℹ️  Le modèle qwen2.5:1.5b sera téléchargé automatiquement si nécessaire"

# Définir les variables d'environnement
export OLLAMA_HOST=0.0.0.0:8000
export OLLAMA_MODELS=/usr/share/ollama/.ollama/models

echo ""
echo "✅ Configuration:"
echo "   - Port: 8000"
echo "   - Modèle: qwen2.5:1.5b"
echo "   - NPU: Hailo-10H (/dev/hailo0)"
echo ""
echo "🧠 Démarrage de hailo-ollama..."
echo "   ⏳ Attendez de voir: 'Listening on 0.0.0.0:8000 (version X.X.X)'"
echo "   (Ctrl+C pour arrêter)"
echo ""

# Démarrer hailo-ollama en mode serveur
exec hailo-ollama serve
