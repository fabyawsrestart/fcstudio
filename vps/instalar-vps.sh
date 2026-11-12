#!/usr/bin/env bash
# Instalação completa da VPS FC Studio (Ubuntu 24.04, DigitalOcean).
# Rodar como root, de dentro da pasta vps:  bash instalar-vps.sh
# Pode rodar de novo sem medo: o que já existe é mantido (senhas, dados).
set -euo pipefail

cd "$(dirname "$0")"
VPS_DIR="$(pwd)"
AGENDA_REPO="${AGENDA_REPO:-https://github.com/fabyawsrestart/Projetos---FCStudio.git}"

verde() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
amarelo() { printf '\033[1;33m%s\033[0m\n' "$*"; }
erro() { printf '\033[1;31mERRO: %s\033[0m\n' "$*"; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "rode como root (ssh root@IP)."
. /etc/os-release
[ "$ID" = "ubuntu" ] || erro "este script é para Ubuntu (achei: $PRETTY_NAME)."
echo "Sistema: $PRETTY_NAME | Arquitetura: $(uname -m)"

# ---------------------------------------------------------------- 1. Pacotes
verde "1/7 Atualizando o sistema"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
# Mantém arquivos de config locais sem perguntar ("keep the local version")
apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade -y
apt-get install -y ca-certificates curl git openssl ufw

# ---------------------------------------------------------------- 2. Docker
verde "2/7 Instalando Docker + Docker Compose (repositório oficial)"
if ! command -v docker >/dev/null || ! docker compose version >/dev/null 2>&1; then
  # Remove pacotes antigos que conflitam com o Docker oficial (ex.: docker.io)
  for p in docker.io docker-doc docker-compose podman-docker containerd runc; do
    apt-get remove -y "$p" >/dev/null 2>&1 || true
  done
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
systemctl enable --now docker
docker --version
docker compose version

# ---------------------------------------------------------------- 3. Segurança e memória
verde "3/7 Firewall (SSH, HTTP, HTTPS) e memória swap"
ufw allow OpenSSH >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw allow 443/udp >/dev/null
ufw --force enable
# Atenção: o Docker publica portas por fora do ufw. Por isso só o Caddy expõe portas.

if ! swapon --show | grep -q .; then
  RAM_MB=$(free -m | awk '/Mem:/{print $2}')
  if [ "$RAM_MB" -lt 6000 ]; then
    fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Swap de 2 GB criado (evita o servidor travar por falta de memória)."
  fi
fi

# ---------------------------------------------------------------- 4. Configuração (.env)
verde "4/7 Configurando domínios e senhas"
if [ ! -f .env ]; then
  amarelo "Os domínios PRECISAM estar apontados (registro A) para o IP desta VPS antes de continuar."
  amarelo "Deixe em branco o que ainda não for usar."
  read -rp "E-mail para avisos do certificado HTTPS: " ACME_EMAIL
  read -rp "Domínio do n8n (ex: n8n.fcstudio.com.br): " DOMAIN_N8N
  read -rp "Domínio da agenda do cliente (ex: agenda.clinicavitalle.com.br): " DOMAIN_AGENDA
  read -rp "Domínio do site WordPress (ex: fcstudio.com.br) [opcional]: " DOMAIN_SITE
  [ -n "$DOMAIN_N8N" ] || erro "o domínio do n8n é obrigatório (é a base da instalação)."

  umask 077
  cat > .env <<EOF
ACME_EMAIL=$ACME_EMAIL
DOMAIN_N8N=$DOMAIN_N8N
DOMAIN_AGENDA=$DOMAIN_AGENDA
DOMAIN_SITE=$DOMAIN_SITE

POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=$(openssl rand -hex 24)
N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)
N8N_VERSION=stable

WP_DB_PASSWORD=$(openssl rand -hex 24)
WP_DB_ROOT_PASSWORD=$(openssl rand -hex 24)
WP_TABLE_PREFIX=wp_

TZ=America/Sao_Paulo
EOF
  umask 022
  echo ".env criado. Senhas geradas automaticamente."
else
  echo ".env já existe, mantendo (para mudar domínios: nano .env e rode este script de novo)."
fi
set -a; . ./.env; set +a
grep -v 'PASSWORD\|ENCRYPTION_KEY' .env

# ---------------------------------------------------------------- 5. Sites no Caddy
verde "5/7 Gerando configuração do proxy (Caddy + HTTPS automático)"
rm -f caddy/sites/*.caddy
cat > caddy/sites/n8n.caddy <<EOF
$DOMAIN_N8N {
	reverse_proxy n8n:5678 {
		flush_interval -1
	}
}
EOF

if [ -n "${DOMAIN_AGENDA:-}" ]; then
  verde "Baixando a agenda do cliente"
  # Repositório privado? O git pede usuário do GitHub e um token (não a senha).
  git config --global credential.helper 'cache --timeout=3600'
  if [ -d apps/agenda/.git ]; then git -C apps/agenda pull --ff-only
  else mkdir -p apps && git clone --depth 1 "$AGENDA_REPO" apps/agenda; fi
  mkdir -p www/agenda
  cp "apps/agenda/Agenda Clínica Vitalle.html" www/agenda/index.html
  cat > caddy/sites/agenda.caddy <<EOF
$DOMAIN_AGENDA {
	root * /srv/agenda
	encode zstd gzip
	file_server
	header {
		X-Content-Type-Options nosniff
		Referrer-Policy strict-origin-when-cross-origin
	}
}
EOF
fi

PROFILES=""
if [ -n "${DOMAIN_SITE:-}" ]; then
  PROFILES="--profile wordpress"
  cat > caddy/sites/site.caddy <<EOF
$DOMAIN_SITE {
	encode zstd gzip
	reverse_proxy wordpress:80
}
EOF
  # www.dominio -> dominio (precisa do registro www apontando pra VPS)
  case "$DOMAIN_SITE" in
    www.*) ;;
    *) cat >> caddy/sites/site.caddy <<EOF

www.$DOMAIN_SITE {
	redir https://$DOMAIN_SITE{uri} permanent
}
EOF
    ;;
  esac
fi
ls caddy/sites

# ---------------------------------------------------------------- 6. Subir tudo
verde "6/7 Validando e subindo os containers"
docker compose $PROFILES config --quiet
docker compose $PROFILES pull
docker compose $PROFILES up -d --remove-orphans
echo "$PROFILES" > .profiles

# ---------------------------------------------------------------- 7. Conferência
verde "7/7 Conferindo"
sleep 15
docker compose $PROFILES ps
echo
for d in "$DOMAIN_N8N" "${DOMAIN_AGENDA:-}" "${DOMAIN_SITE:-}"; do
  [ -n "$d" ] || continue
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "https://$d" || true)
  echo "https://$d  ->  HTTP $code"
done
cat <<EOF

Pronto. Se algum domínio deu 000, o DNS ainda não propagou ou não aponta para
este IP ($(curl -s --max-time 5 https://api.ipify.org || echo 'veja no painel')).
O Caddy tenta de novo sozinho; confira com: docker compose logs -f caddy

Próximo passo: abra https://$DOMAIN_N8N e crie a conta de dono do n8n AGORA
(quem abrir primeiro vira o administrador).
EOF
