#!/usr/bin/env bash
# Backup dos bancos e arquivos. Guarda os últimos 7 em /opt/backups.
# Uso: bash backup.sh   (agendado todo dia às 3h pelo comando do README)
set -euo pipefail
cd "$(dirname "$0")"
set -a; . ./.env; set +a
DEST=${BACKUP_DIR:-/opt/backups}/$(date +%F_%H%M)
mkdir -p "$DEST"

docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$DEST/n8n-postgres.sql.gz"
docker run --rm -v "fcstudio_n8n_data:/d:ro" -v "$DEST:/b" alpine tar czf /b/n8n-data.tgz -C /d .

if docker compose ps --services --status running | grep -q '^mariadb$'; then
  docker compose exec -T mariadb mariadb-dump -u root -p"$WP_DB_ROOT_PASSWORD" --single-transaction wordpress | gzip > "$DEST/wordpress.sql.gz"
  docker run --rm -v "fcstudio_wordpress_data:/d:ro" -v "$DEST:/b" alpine tar czf /b/wordpress-files.tgz -C /d .
fi

cp .env "$DEST/env.backup" && chmod 600 "$DEST/env.backup"
ls -1dt "${BACKUP_DIR:-/opt/backups}"/*/ | tail -n +8 | xargs -r rm -rf
du -sh "$DEST"
