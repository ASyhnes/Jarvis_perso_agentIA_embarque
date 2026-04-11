# 🤖 Jarvis-BMO (Version 3.0 - Dual Brain)

![Status](https://img.shields.io/badge/Status-Actif-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Raspberry_Pi_5_%7C_PC-blue)
![AI](https://img.shields.io/badge/AI-Ollama_%7C_Gemma_%7C_Llama-orange)

**Agent IA hybride : Local-First & Cloud-Local (PC de calcul)**  
Plateforme : Raspberry Pi 5 (8 Go) & PC déporté  
Philosophie : Éthique Kantienne & Zététique (Esprit Critique)

---

## ⚠️ Origine du Projet & Avertissement

Ce projet est très inspiré du projet initial de brenpoly. J'ai notamment repris certaines images de son projet open source pour l'interface. Néanmoins, j'ai choisi d'opérer une **refonte complète** du projet : je ne conserve que l'idée fondatrice de l'assistant IA sur Raspberry Pi, mais j'ai choisi de repenser entièrement la structure fondamentale et l'architecture analytique (intégration de la rêverie, prise de recul déportée, double cerveau Kantien/Zététique...).

---

## 🎭 Les Visages de Jarvis-BMO



<p align="center">
  <img src="faces/capturing/capturing%2001.png" alt="Visage Capture" width="200"/>
  <img src="faces/speaking/speaking%2001.png" alt="Visage Parole 1" width="200"/>
  <img src="faces/speaking/speaking%2002.png" alt="Visage Parole 2" width="200"/>
</p>

<p align="center">
  <img src="faces/unnamed%20(1).jpg" alt="Visage Unnamed" width="200"/>
</p>

*(Note : J'ai également ajouté tous les visages de parole présents dans le dossier `faces/speaking` pour une galerie plus complète)*
---

## 🧠 1. Vision du Projet : Le "Cerveau Double"

Le projet Jarvis-BMO repose sur une architecture novatrice de **Cerveau Double**. Cette structure imite la psychologie cognitive en séparant l'instinct immédiat de la réflexion profonde.

*   **L'Hémisphère Intuitif (Raspberry Pi) :** Gère le quotidien, les interactions sociales rapides, les blagues et les tâches domotiques simples. C'est le Jarvis "attachant" et espiègle.
*   **L'Hémisphère Critique (PC Performant) :** Gère l'analyse complexe, la recherche documentaire approfondie et l'application stricte de la zététique. C'est le Jarvis "philosophe et savant".

---

## 🔄 2. Architecture et Connexion (Prise de recul)

L'agent dispose d'une fonction unique de **Prise de Recul**. Lorsqu'il est connecté au Wi-Fi, il peut déléguer sa conscience à un duplicata plus puissant hébergé sur un ordinateur de bureau.

**Déclencheurs du passage en mode Critique :**
*   **Mode Sommeil :** Pendant que le Raspberry Pi est en veille, l'agent utilise la puissance du PC pour synthétiser les discussions de la journée ou organiser sa mémoire à long terme.
*   **Besoin d'Esprit Critique :** Si l'utilisateur pose une question complexe nécessitant une vérification des faits (*Fact-checking*) ou une analyse philosophique lourde, l'agent bascule automatiquement vers le PC.
*   **Accès aux Outils :** L'agent sur PC possède des capacités de recherche web étendues et peut traiter des documents massifs.

### 🌙 Le Processus de "Rêve" et l'Esprit Critique

Le concept du **Cerveau Double** prend tout son sens dans la gestion de la mémoire à long terme et de la réflexion profonde. Pour éviter de surcharger l'agent local, le système s'inspire directement du cycle cognitif humain :

*   **La Phase de Rêve (Consolidation nocturne) :** Lorsque Jarvis-BMO entre en "Mode Veille" (la nuit ou lors de longues périodes d'inactivité), le Raspberry Pi transfère les journaux de conversation bruts de la journée au PC déporté. Le PC lance alors un processus de "rêve" en arrière-plan. Il relit les interactions, synthétise les informations clés, supprime les faits obsolètes ou contredits, et met à jour proprement le fichier d'indexation (`memory.json`). Cette hygiène mentale évite la surcharge cognitive (le "bruit") et permet à l'agent de se réveiller avec une mémoire fraîche et structurée.
*   **L'Éveil de l'Esprit Critique :** En phase d'éveil, si une discussion requiert de la nuance, un fact-checking rigoureux ou aborde un dilemme moral, l'agent intuitif (le Pi) délègue la tâche. L'agent déporté (le PC) prend alors le relais avec une double boussole intellectuelle :
    *   *La Zététique :* Application du doute méthodique, exigence de preuves matérielles et identification des biais cognitifs dans la conversation.
    *   *L'Éthique Kantienne :* Recherche d'une morale universelle et d'une logique irréprochable dans les réponses apportées à l'utilisateur.

--- 
### 💡 Note de conception : Sur la bonne piste !

Il s'avère que l'idée d'intégrer un **"Mode Veille"** (où Jarvis-BMO profite de son inactivité pour trier et consolider sa mémoire) était sur la bonne piste ! Preuve en est, une évolution récente dans l'industrie de l'IA vient d'adopter cette même approche. 

Dans une vidéo de la chaîne Vision IA, on découvre qu'Anthropic a discrètement intégré une fonctionnalité nommée **"Auto Dream"** pour son agent autonome Claude Code. 

Le principe expliqué dans la vidéo est exactement celui visé par notre système de Cerveau Double :
* **Le concept du "Sleep Time Compute" :** Pendant ses phases d'inactivité, l'IA lance un sous-agent en arrière-plan pour "rêver". 
* **Tri et consolidation :** Tout comme le cerveau humain en phase de sommeil paradoxal, l'IA relit ses notes des sessions passées, supprime les faits contredits, convertit les données temporelles et reconstruit un index propre.
* **Prévention de la surcharge :** Cela évite que l'IA ne finisse noyée dans un "bruit" d'informations contradictoires au fil du temps.

Cela confirme que l'architecture de Jarvis (où le Raspberry Pi délègue la compilation de sa journée au PC pendant la nuit) répond à une vraie problématique et s'inscrit totalement dans les enjeux actuels d'optimisation des systèmes multi-agents.

### 🧠 Claude Code : Fonctionnalité "Auto Dream"

### 📖 Qu'est-ce que Auto Dream ?

**Auto Dream** est un mécanisme expérimental de consolidation de mémoire en arrière-plan développé par Anthropic pour son assistant développeur **Claude Code**.

Inspiré du concept de "Sleep Time Compute" et du sommeil humain, cette fonctionnalité profite des périodes d'inactivité de l'IA (entre les sessions de développement) pour nettoyer, réorganiser et dédoublonner ses propres fichiers de prise de notes. 

Ce processus permet de résoudre le problème d'obésité de la mémoire (*Memory Bloat*) où l'IA finit par se contredire après des dizaines de sessions. Auto Dream s'assure que le contexte reste propre, synthétique et pertinent pour les futures interactions.

### ⚙️ Le cycle de consolidation en 4 phases :
1. **Orientation** : Lecture de l'état actuel du répertoire mémoire pour comprendre le contexte existant.
2. **Collecte** : Scan des sessions récentes pour repérer les nouvelles décisions d'architecture, les corrections de bugs et les changements de préférences.
3. **Consolidation** : Fusion des nouvelles informations avec les anciennes. L'agent convertit les dates relatives (ex: "hier") en dates absolues et supprime les faits devenus obsolètes ou contradictoires.
4. **Élagage** : Reconstruction de l'index principal (ex: `memory.md`) pour le maintenir sous un seuil optimal (souvent autour de 200 lignes) afin de garantir de bonnes performances sans surcharger le contexte.

---

## 🔗 Sources et Ressources

### 📺 Vidéos explicatives
* [**Vision IA - Claude contrôle votre ordinateur pendant que vous dormez (et il RÊVE la nuit)**](https://www.youtube.com/watch?v=KG4J68WBc3A)
  > *Explication détaillée du système de rêve / Auto Dream à partir de [10:35].*

### 📚 Articles et Documentation technique
* [**SFEIR Institute : Claude Code Dream & Auto Dream - Automatic Memory Consolidation**](https://institute.sfeir.com/en/articles/claude-code-dream-auto-dream-memory-consolidation/)
  > *Analyse technique approfondie du fonctionnement sous le capot et du cycle en 4 phases.*

* [**MindStudio : What Is Claude Code AutoDream? How AI Memory Consolidation Works Like Sleep**](https://www.mindstudio.ai/blog/what-is-claude-code-autodream-memory-consolidation-2)
  > *Vulgarisation du concept biomimétique d'Auto Dream et de la façon dont l'IA utilise son inactivité pour améliorer ses performances.*

* [**Implicator.ai : Anthropic Adds Auto Dream to Claude Code, Fixing Memory Decay Between Sessions**](https://www.implicator.ai/anthropic-adds-auto-dream-to-claude-code-fixing-memory-decay-between-sessions/)
  > *Article traitant du déploiement expérimental de la fonctionnalité et de son impact réel sur la dégradation de la mémoire à long terme.*
---

## 🗣️ 3. Les Deux Modes de Discussion

### A. Discussion Intuitive (Mode Local)
*   **Hébergement :** Raspberry Pi 5
*   **Modèle :** `qwen2.5:3b` ou `gemma3:1b`
*   **Caractéristique :** Réponses ultra-rapides, ton oral, espièglerie
*   **Rôle :** Compagnon domestique, gestion du temps, météo, conversation de surface

### B. Discussion Critique (Mode Déporté)
*   **Hébergement :** Ordinateur plus performant (via connexion Wi-Fi/SSH)
*   **Modèle :** `llama3:8b`, `qwen2.5:7b` ou supérieur
*   **Caractéristique :** Analyse zététique poussée, scepticisme méthodique, recherche de preuves
*   **Rôle :** Aide à la décision, débats kantiens, recherche scientifique, déconstruction de *fake news*

---

## ⚙️ 4. Spécifications Matérielles (Hardware)

| Composant | Détails Actuels | Évolution Future |
| :--- | :--- | :--- |
| **Unité Centrale** | Raspberry Pi 5 (8 Go RAM) | + Hailo-10L (Top NPU) |
| **Calcul IA** | CPU / GPU intégré | NPU Hailo (jusqu'à 40 TOPS) |
| **Microphone** | USB PnP (Index 1) | *Idem* |
| **Haut-parleur** | Jack / USB via Piper TTS | *Idem* |
| **Cerveau Distant**| PC Windows/Linux (Ollama) | Cluster local / GPU dédié |

> 💡 **Focus : Intégration du Hailo-10L**  
> L'ajout futur du module d'accélération matérielle Hailo-10L permettra d'augmenter radicalement la puissance de l'agent intuitif local :
> *   **Vitesse :** Inférence quasi-instantanée (réduction du phénomène de *"Brain Freeze"*).
> *   **Complexité :** Possibilité de faire tourner des modèles plus larges (ex: 7B) directement sur le Pi 5 sans latence.
> *   **Vision :** Analyse d'image en temps réel plus fluide (reconnaissance faciale, détection d'objets).

---

## 🛠️ 5. Logique du Code et Indentation (Rappel Technique)

L'agent utilise une classe Python `BotGUI` structurée pour éviter les plantages de la carte son (ALSA).

*   **Gestion des erreurs :** Le bloc `detect_wake_word_or_ptt` est configuré pour isoler l'index du micro USB et basculer automatiquement en mode clavier (PTT - *Push To Talk*) si le flux audio s'interrompt.
*   **Synchronisation :** Le script `agent.py` vérifie en permanence la disponibilité de l'IP du PC. Si le PC est éteint, l'agent reste de manière autonome en mode "Intuitif" pur.

---

## 📜 6. Philosophie Intégrée (Modelfile)

Le paramétrage comportemental (Modelfile) de l'agent critique diffère radicalement de celui de l'agent intuitif. 
Note: le SYSTEM présenté ici n'est qu'un embryon du vrai system prompt à venir plus tard.

```dockerfile
# Modelfile Critique (Hébergé sur PC)
FROM qwen2.5:7b
SYSTEM """
Tu es l'Esprit Critique de Jarvis-BMO. 
Tu interviens pour David lors des phases de réflexion profonde.
Ton socle est la Zététique : demande des preuves, analyse les biais.
Ton cadre est Kant : cherche l'universel.
Contrairement à l'agent intuitif, tu es autorisé à faire des analyses longues et sourcées.
"""
```
---

## 🔧 7. Structure de Maintenance

Développement : Toujours effectué via Cursor ou VS Code en SSH.

Mise à jour des modèles :

ollama pull qwen2.5:3b (sur le Pi 5)

ollama pull qwen2.5:7b (sur le PC de calcul)

Backup : Le fichier memory.json est synchronisé en réseau entre les deux cerveaux pour garantir une continuité et une personnalité cohérente, quel que soit le mode actif.

---

##  🗺️ 8. Roadmap & Évolutions
Voici la feuille de route du développement de Jarvis-BMO, depuis son prototype actuel jusqu'à l'intégration complète du Cerveau Double.

### 🟢 Phase 1 : Le "Prequel" (État Actuel)
- [x] **Base Opérationnelle (Python) :** L'assistant est capable d'entendre, de parler et possède son propre moteur de réflexion interactif.
- [x] **Boucle audio :** Intégration du STT (Speech-to-Text) et du TTS (Text-to-Speech) fonctionnelle.

### 🟡 Phase 2 : Refonte & Optimisation
- [ ] **Migration vers C++ :** Le code Python actuel étant trop gourmand, réécriture du cœur du programme en C++. L'objectif est de réduire drastiquement l'empreinte mémoire et d'optimiser l'utilisation des ressources du Raspberry Pi.

### 🟠 Phase 3 : Nouvelles Capacités (Sens & Contexte)
- [ ] **L'Ajout de la Vue :** Intégration d'un système de vision par ordinateur en C++ (équivalent des bibliothèques Python d'analyse d'image) pour permettre à l'agent d'analyser son environnement visuel.
- [ ] **Mémoire Conversationnelle :** Création d'un historique de contexte persistant, permettant à l'agent de se souvenir du fil des discussions passées.

### 🔴 Phase 4 : Déploiement du Cerveau Double
- [ ] **Mode Veille (Sleep Mode) :** Implémentation d'une routine où l'agent stocke sa mémoire locale et l'envoie vers l'ordinateur plus performant. Le PC effectuera alors un tri et une synthèse de tout ce qui a été enregistré dans la journée.
- [ ] **Mode Réflexion Critique :** Activation du système de prise de recul lorsque la discussion devient sérieuse>. détection de notion fondamentale sur la définition du "sérieux" d'une discussion.

### 🟣 Phase 5 : Trading & Sécurité
- [ ] Mettre en place open claw
- [ ] Sécuriser en faisant ce qu'il faut
- [ ] Prévoir l'installation du système de trading
- [ ] Affichage d'un tableau de bord des différents outils/stratégies de trading
- [ ] Préparer la possibilité de gérer mes stratégies en discutant avec Jarvis
