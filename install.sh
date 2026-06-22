#!/usr/bin/env bash
set -euo pipefail

force=0
if [[ "${1:-}" == "--force" ]]; then
  force=1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="$repo_root/skills/game-ui-asset-pipeline"
if [[ ! -d "$source_dir" ]]; then
  echo "Skill source not found: $source_dir" >&2
  exit 1
fi

codex_home="${CODEX_HOME:-$HOME/.codex}"
dest_parent="$codex_home/skills"
dest="$dest_parent/game-ui-asset-pipeline"
mkdir -p "$dest_parent"

if [[ -e "$dest" ]]; then
  if [[ "$force" != "1" ]]; then
    echo "Destination already exists: $dest. Re-run with --force to replace it." >&2
    exit 1
  fi
  rm -rf "$dest"
fi

cp -R "$source_dir" "$dest"
echo "Installed game-ui-asset-pipeline to $dest"
echo "Restart Codex to pick up the skill."
