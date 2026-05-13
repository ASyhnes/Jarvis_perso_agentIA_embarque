#!/usr/bin/env bash
set -euo pipefail

DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="archive/phase1_$DATE"
mkdir -p "$ARCHIVE_DIR"

echo "Archive destination: $ARCHIVE_DIR"

# Archive top-level directories that look like backups or scratch copies
for p in agent-v2.backup-* scratch_original_repo*; do
  if [ -e "$p" ]; then
    echo "Archiving $p"
    tar -czf "$ARCHIVE_DIR/${p%/}.tar.gz" "$p"
    rm -rf "$p"
  fi
done

# Archive any directories in the workspace matching common backup patterns
shopt -s nullglob
for d in */; do
  case "$d" in
    *backup*|*BACKUP*|scratch*/|*old*/)
      name=${d%/}
      echo "Archiving $name"
      tar -czf "$ARCHIVE_DIR/${name}.tar.gz" "$d"
      rm -rf "$d"
      ;;
  esac
done
shopt -u nullglob

# Clean python cache files
echo "Removing .pyc and __pycache__ files"
find . -type f -name '*.pyc' -delete || true
find . -type d -name '__pycache__' -exec rm -rf {} + || true

echo "Phase 1 archive & cleanup complete. Archives stored in $ARCHIVE_DIR"
