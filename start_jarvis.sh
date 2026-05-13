#!/bin/bash
# ============================================================================
# Script de démarrage de Jarvis-BMO V2
# ============================================================================

echo "🤖 Démarrage de Jarvis-BMO V2..."

# Chemin vers le projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ ERREUR: L'environnement virtuel n'existe pas"
    echo "   Exécutez d'abord: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Vérifier que hailo-ollama est accessible
echo "🔍 Vérification de hailo-ollama..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -s http://127.0.0.1:8000/api/tags > /dev/null 2>&1; then
        echo "✅ hailo-ollama est accessible"
        break
    fi
    echo "⏳ En attente de hailo-ollama... ($retry_count/$max_retries)"
    sleep 2
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ ERREUR: hailo-ollama n'est pas accessible après 60 secondes"
    echo "   Assurez-vous que le service bmo-ollama est démarré"
    exit 1
fi

# Configuration de l'environnement graphique (pour Raspberry Pi)
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-1
export XDG_RUNTIME_DIR=/run/user/$(id -u)

echo ""
echo "✅ Configuration:"
echo "   - Environnement: venv"
echo "   - Dossier: $PROJECT_DIR"
echo "   - Agent: agent-v2/main.py"
echo ""
echo "🚀 Démarrage de Jarvis-BMO V2..."
echo "   (Les logs seront dans /var/log/jarvis-bmo.log)"
echo ""

# Démarrer Jarvis avec l'environnement virtuel
cd "$PROJECT_DIR/agent-v2"
exec "$PROJECT_DIR/venv/bin/python" main.py
