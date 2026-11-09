#!/usr/bin/env bash
# Atualiza tudo: código da agenda, imagens (n8n, Caddy, WordPress...) e reinicia o que mudou.
# Uso: bash atualizar.sh
set -euo pipefail
cd "$(dirname "$0")"
PROFILES="$(cat .profiles 2>/dev/null || true)"

git pull --ff-only || echo "Aviso: não consegui atualizar o repositório fcstudio."
if [ -d apps/agenda/.git ]; then
  git -C apps/agenda pull --ff-only
  cp "apps/agenda/Agenda Clínica Vitalle.html" www/agenda/index.html
  echo "Agenda atualizada."
fi

bash backup.sh   # backup antes de trocar versões
docker compose $PROFILES pull
docker compose $PROFILES up -d --remove-orphans
docker image prune -f >/dev/null
docker compose $PROFILES ps
