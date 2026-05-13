# 🚀 Guide de Lancement Manuel de Jarvis-BMO V2

## 📌 Changements Récents

Jarvis-BMO ne démarre **PLUS automatiquement** au démarrage du Raspberry Pi.  
Vous avez maintenant un **contrôle total** sur le lancement et l'arrêt de l'assistant vocal.

---

## 🖱️ Lancer Jarvis-BMO

### Méthode 1 : Icône sur le Bureau (RECOMMANDÉ)
1. **Double-cliquez** sur l'icône **"Jarvis-BMO V2"** sur votre bureau
2. Un terminal s'ouvrira et Jarvis démarrera automatiquement
3. Attendez que Jarvis soit en veille (état "SLEEP")
4. Dites **"debout là dedans"** ou **"jarvis"** pour le réveiller

### Méthode 2 : Terminal
```bash
cd /home/syhnes/be-more-agent
./start_jarvis.sh
```

### Méthode 3 : Service systemd
```bash
sudo systemctl start jarvis-bmo.service
```

---

## 🛑 Arrêter Jarvis-BMO

### Méthode 1 : Commande Vocale (NOUVELLE FONCTIONNALITÉ !)
Dites simplement l'une de ces phrases :
- **"stop jarvis"**
- **"arrête jarvis"**
- **"éteins jarvis"**

Jarvis répondra "D'accord, je m'arrête. À bientôt !" et s'éteindra complètement.

### Méthode 2 : Terminal
Si vous avez lancé Jarvis dans un terminal :
- Appuyez sur **Ctrl+C**

### Méthode 3 : Service systemd
```bash
sudo systemctl stop jarvis-bmo.service
```

---

## 🎤 Commandes Vocales Disponibles

### Réveil
- **"debout là dedans"**
- **"jarvis"**
- **"bimo"**
- **"debout"**
- **"alexa"**

### Mise en Veille (Jarvis reste actif mais n'écoute que le mot de réveil)
- **"dors"**
- **"merci"**
- **"sommeil"**

### Arrêt Complet (Jarvis s'éteint complètement)
- **"stop jarvis"** ⭐ NOUVEAU
- **"arrête jarvis"** ⭐ NOUVEAU
- **"éteins jarvis"** ⭐ NOUVEAU

---

## 💡 Conseils d'Utilisation

### Pour un usage quotidien
1. **Lancement** : Double-cliquez sur l'icône du bureau le matin
2. **Utilisation** : Discutez avec Jarvis normalement
3. **Arrêt** : Dites "stop jarvis" le soir avant de vous coucher

### Pour les tests/développement
1. Lancez Jarvis en terminal : `./start_jarvis.sh`
2. Surveillez les logs en temps réel
3. Arrêtez avec Ctrl+C pour un arrêt rapide

### Pour réactiver le démarrage automatique (si besoin)
```bash
sudo systemctl enable jarvis-bmo.service
```
Puis au prochain redémarrage, Jarvis démarrera automatiquement.

---

## 🔍 Vérifier l'État de Jarvis

### Vérifier si Jarvis tourne
```bash
systemctl status jarvis-bmo.service
```

### Voir les logs en temps réel
```bash
sudo journalctl -u jarvis-bmo.service -f
```

---

## ✅ Avantages du Lancement Manuel

✅ **Économie de ressources** : Le Raspberry Pi démarre plus rapidement  
✅ **Contrôle total** : Vous décidez quand Jarvis doit être actif  
✅ **Arrêt facile** : Simple commande vocale pour éteindre  
✅ **Pas de processus fantôme** : Jarvis ne tourne que quand vous en avez besoin  

---

## 📂 Fichiers Modifiés

- ✅ Service désactivé : `jarvis-bmo.service` ne démarre plus au boot
- ✅ Icône créée : `/home/syhnes/Desktop/Jarvis-BMO.desktop`
- ✅ Commande vocale ajoutée : `agent-v2/wakeword.py` (fonction `check_sleep_command`)
- ✅ Documentation mise à jour : `GUIDE_SERVICES.md`

---

**🎉 Profitez de votre contrôle total sur Jarvis-BMO V2 !**
