# Guide de Gestion des Services Jarvis-BMO

## 📋 Vue d'ensemble

Jarvis-BMO fonctionne avec **2 services systemd** qui démarrent automatiquement au boot :

1. **bmo-ollama.service** : Serveur LLM Hailo-Ollama (port 8000)
2. **jarvis-bmo.service** : Assistant vocal Jarvis-BMO V2

Les services sont configurés pour démarrer dans l'ordre : d'abord hailo-ollama, puis Jarvis.

---

## 🎮 Commandes Essentielles

### Démarrer les services
```bash
sudo systemctl start bmo-ollama.service
sudo systemctl start jarvis-bmo.service
```

### Arrêter les services
```bash
sudo systemctl stop jarvis-bmo.service
sudo systemctl stop bmo-ollama.service
```

### Redémarrer les services
```bash
sudo systemctl restart bmo-ollama.service
sudo systemctl restart jarvis-bmo.service
```

### Vérifier le statut
```bash
systemctl status bmo-ollama.service
systemctl status jarvis-bmo.service
```

### Voir les logs en temps réel
```bash
# Logs de hailo-ollama
sudo journalctl -u bmo-ollama.service -f

# Logs de Jarvis
sudo journalctl -u jarvis-bmo.service -f

# Les deux en même temps
sudo journalctl -u bmo-ollama.service -u jarvis-bmo.service -f
```

### Voir les logs historiques
```bash
# Dernières 100 lignes
sudo journalctl -u jarvis-bmo.service -n 100

# Depuis aujourd'hui
sudo journalctl -u jarvis-bmo.service --since today

# Depuis une heure spécifique
sudo journalctl -u jarvis-bmo.service --since "2026-05-07 14:00:00"
```

---

## 🔄 Configuration du Démarrage Automatique

### ⚠️ STATUT ACTUEL : Démarrage manuel uniquement

**Jarvis-BMO ne démarre PLUS automatiquement au démarrage du Raspberry Pi.**

Pour lancer Jarvis, utilisez :
- **Double-cliquez sur l'icône "Jarvis-BMO V2"** sur le bureau
- OU en ligne de commande : `./start_jarvis.sh` depuis `/home/syhnes/be-more-agent/`
- OU via systemd : `sudo systemctl start jarvis-bmo.service`

Pour arrêter Jarvis :
- **Commande vocale** : Dites "**stop jarvis**" (ou "arrête jarvis", "éteins jarvis")
- OU via systemd : `sudo systemctl stop jarvis-bmo.service`
- OU Ctrl+C dans le terminal

### Activer le démarrage automatique (si besoin)
```bash
sudo systemctl enable bmo-ollama.service
sudo systemctl enable jarvis-bmo.service
```

### Désactiver le démarrage automatique (déjà fait ✅)
```bash
sudo systemctl disable jarvis-bmo.service
sudo systemctl disable bmo-ollama.service
```

### Vérifier si le démarrage automatique est activé
```bash
systemctl is-enabled bmo-ollama.service
systemctl is-enabled jarvis-bmo.service
```

---

## 🛠️ Maintenance et Dépannage

### Recharger les services après modification
Si vous modifiez les fichiers `.service`, rechargez systemd :
```bash
sudo systemctl daemon-reload
sudo systemctl restart bmo-ollama.service
sudo systemctl restart jarvis-bmo.service
```

### Vérifier l'ordre de démarrage
```bash
systemctl list-dependencies jarvis-bmo.service
```

### Tester le démarrage manuel
Si vous voulez tester sans systemd :
```bash
# Terminal 1 : Démarrer hailo-ollama
cd /home/syhnes/be-more-agent
./start_hailo_ollama.sh

# Terminal 2 : Démarrer Jarvis
cd /home/syhnes/be-more-agent
./start_jarvis.sh
```

---

## 📍 Emplacements des Fichiers

- **Services systemd** : `/etc/systemd/system/`
  - `bmo-ollama.service`
  - `jarvis-bmo.service`

- **Scripts de démarrage** : `/home/syhnes/be-more-agent/`
  - `start_hailo_ollama.sh`
  - `start_jarvis.sh`

- **Logs système** : Accessibles via `journalctl`

---

## 🚀 Démarrage Rapide

Pour démarrer Jarvis maintenant (sans redémarrer) :
```bash
sudo systemctl start bmo-ollama.service
sudo systemctl start jarvis-bmo.service
```

Pour tout arrêter :
```bash
sudo systemctl stop jarvis-bmo.service bmo-ollama.service
```

Pour vérifier que tout fonctionne :
```bash
systemctl status bmo-ollama.service jarvis-bmo.service
```

---

## ✅ Statut de Configuration

✅ **Services créés** : bmo-ollama.service, jarvis-bmo.service  
⚠️ **Démarrage automatique désactivé** : Jarvis ne démarre PLUS au boot  
✅ **Icône bureau** : Double-cliquez sur "Jarvis-BMO V2" pour lancer  
✅ **Commande vocale d'arrêt** : "stop jarvis" pour éteindre complètement  
✅ **Scripts de démarrage** : start_hailo_ollama.sh, start_jarvis.sh  
✅ **Permissions** : Scripts exécutables, services installés  

---

## 🎤 Commandes Vocales Disponibles

- **"debout là dedans"** / **"jarvis"** / **"bimo"** : Réveiller Jarvis
- **"dors"** / **"merci"** : Mettre Jarvis en veille (écoute uniquement le mot de réveil)
- **"stop jarvis"** / **"arrête jarvis"** / **"éteins jarvis"** : Arrêter complètement Jarvis

**Jarvis ne démarrera PLUS automatiquement. Lancez-le manuellement via l'icône du bureau ! 🖱️**
