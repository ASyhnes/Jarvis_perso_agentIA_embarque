# Phase 1 — Archivage et Nettoyage

Objectif
- Archiver les répertoires de sauvegarde et copies anciennes
- Supprimer les fichiers caches Python inutiles

Comportement du script
- Le script `tools/phase1_archive_cleanup.sh` crée `archive/phase1_YYYYMMDD_HHMMSS/`
- Il compresse et supprime les dossiers correspondants aux motifs `agent-v2.backup-*`, `scratch_original_repo*`, et autres répertoires contenant `backup`, `scratch` ou `old`.
- Il supprime les fichiers `*.pyc` et les dossiers `__pycache__`.

Usage
```
bash tools/phase1_archive_cleanup.sh
```

Vérification
- Inspecter le dossier `archive/` créé
- Valider que rien d'essentiel n'a été archivé avant suppression

Remarque
- Exécuter ce script localement après revue; il supprime des fichiers/dossiers.
