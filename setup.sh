#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Script d'installation de l'assistant local Pi${NC}"

# 1. Install System Dependencies (The "Hidden" Requirements)
echo -e "${YELLOW}[1/6] Installation des outils système (apt)...${NC}"
sudo apt update
sudo apt install -y python3-tk libasound2-dev libportaudio2 libatlas-base-dev cmake build-essential espeak-ng git

# 2. Create Folders
echo -e "${YELLOW}[2/6] Création des dossiers...${NC}"
mkdir -p piper
mkdir -p sounds/greeting_sounds
mkdir -p sounds/thinking_sounds
mkdir -p sounds/ack_sounds
mkdir -p sounds/error_sounds
mkdir -p faces/idle
mkdir -p faces/listening
mkdir -p faces/thinking
mkdir -p faces/speaking
mkdir -p faces/error
mkdir -p faces/warmup

# 3. Download Piper (Architecture Check)
echo -e "${YELLOW}[3/6] Configuration de Piper TTS...${NC}"
ARCH=$(uname -m)
if [ "$ARCH" == "aarch64" ]; then
    # FIXED: Using the specific 2023.11.14-2 release known to work on Pi
    wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz
    tar -xvf piper.tar.gz -C piper --strip-components=1
    rm piper.tar.gz
else
    echo -e "${RED}⚠️  Pas sur un Raspberry Pi (aarch64). Téléchargement de Piper ignoré.${NC}"
fi

# 4. Download Voice Model
echo -e "${YELLOW}[4/6] Téléchargement du modèle de voix...${NC}"
cd piper
wget -nc -O fr_FR-upmc-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx
wget -nc -O fr_FR-upmc-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json
cd ..

# 5. Install Python Libraries
echo -e "${YELLOW}[5/6] Installation des bibliothèques Python...${NC}"
# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Pull AI Models
echo -e "${YELLOW}[6/6] Vérification des modèles IA...${NC}"
if command -v ollama &> /dev/null; then
    ollama pull gemma3:1b
    ollama pull moondream
else
    echo -e "${RED}❌ Ollama introuvable. Veuillez l'installer manuellement.${NC}"
fi

# 7. OpenWakeWord Model (Added this back so the user has a default)
if [ ! -f "wakeword.onnx" ]; then
    echo -e "${YELLOW}Téléchargement du mot de réveil par défaut 'Hey Jarvis'...${NC}"
    curl -L -o wakeword.onnx https://github.com/dscripka/openWakeWord/raw/main/openwakeword/resources/models/hey_jarvis_v0.1.onnx
fi

echo -e "${GREEN}✨ Installation terminée ! Exécutez 'source venv/bin/activate' puis 'python agent.py'${NC}"
