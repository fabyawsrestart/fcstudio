# Migrar gwmix.ind.br da Hostinger para a VPS

Situação atual do domínio (checado em 12/11/2026):

| Item | Hoje | Depois |
|---|---|---|
| DNS (nameservers) | Hostinger (`ns1/ns2.dns-parking.com`) | **continua na Hostinger** |
| Site | WordPress 6.9 + Elementor 4.3 + Hello Elementor, na hospedagem compartilhada | WordPress no Docker da VPS |
| E-mail (MX) | Hostinger (`mx1/mx2.hostinger.com`) | **não mexer** |

Não precisa de Cloudflare: o DNS já está na Hostinger e é lá que se cria registro e subdomínio.
Trocar nameserver agora só adiciona risco de derrubar o e-mail do cliente.

> ⚠️ **Antes de tudo:** no hPanel, abra **E-mails** e veja se as caixas `@gwmix.ind.br` fazem parte do plano de hospedagem.
> Se fizerem, **não cancele a hospedagem** até mover o e-mail para um plano só de e-mail (Hostinger Email, Google Workspace, Zoho).

---

## 1. Subir a VPS com o site ativado

Siga o `README.md` até o passo 5. Quando o instalador perguntar:

```
Domínio do n8n ............ n8n.SEU-DOMINIO
Domínio da agenda ......... agenda.SEU-DOMINIO
Domínio do site WordPress . gwmix.ind.br
```

Ele já cria `www.gwmix.ind.br` redirecionando para `gwmix.ind.br`.
Nesse momento o HTTPS do `gwmix.ind.br` ainda vai falhar (o DNS aponta para a Hostinger). Normal.

## 2. Baixar o backup da Hostinger

hPanel → **Sites → gwmix.ind.br → Arquivos → Backups**:

- **Backup do banco de dados** → baixe o `.sql.gz`
- **Backup de arquivos** → baixe o `public_html` (zip ou tar.gz)

Anote o prefixo de tabelas: hPanel → Gerenciador de arquivos → `public_html/wp-config.php` → linha `$table_prefix = '...'`.

## 3. Mandar para a VPS (terminal do VS Code, no seu computador)

```bash
ssh root@IP_DO_DROPLET "mkdir -p /opt/migracao"
scp ~/Downloads/NOME-DO-BANCO.sql.gz ~/Downloads/NOME-DOS-ARQUIVOS.zip root@IP_DO_DROPLET:/opt/migracao/
```

## 4. Importar (já dentro da VPS: `ssh root@IP_DO_DROPLET`)

```bash
cd /opt/fcstudio/vps
apt-get install -y unzip

# 4.1 Prefixo de tabelas igual ao antigo (troque wp_abc12_ pelo que você anotou)
sed -i 's/^WP_TABLE_PREFIX=.*/WP_TABLE_PREFIX=wp_abc12_/' .env
set -a; . ./.env; set +a
docker compose --profile wordpress up -d

# 4.2 Arquivos (se o zip vier com a pasta public_html dentro, ajuste o caminho no cp)
mkdir -p /opt/migracao/site && unzip -q /opt/migracao/*.zip -d /opt/migracao/site
ls /opt/migracao/site          # tem que aparecer wp-content, wp-admin...
rm -f /opt/migracao/site/wp-config.php   # o da Hostinger tem a senha do banco de lá
docker compose cp /opt/migracao/site/. wordpress:/var/www/html/
docker compose exec wordpress chown -R www-data:www-data /var/www/html

# 4.3 Banco
gunzip -c /opt/migracao/*.sql.gz | docker compose exec -T mariadb mariadb -u root -p"$WP_DB_ROOT_PASSWORD" wordpress
docker compose exec -T mariadb mariadb -u root -p"$WP_DB_ROOT_PASSWORD" wordpress \
  -e "SELECT option_name, option_value FROM ${WP_TABLE_PREFIX}options WHERE option_name IN ('siteurl','home');"
```

O último comando tem que mostrar `https://gwmix.ind.br` nas duas linhas.

## 5. Virar o DNS (hPanel → Domínios → gwmix.ind.br → DNS / Nameservers)

| Tipo | Nome | Aponta para | Ação |
|---|---|---|---|
| A | `@` | IP do droplet | **editar** (hoje tem 2 registros A da Hostinger: apague os dois e deixe só este) |
| A ou CNAME | `www` | IP do droplet | editar o existente |
| MX, TXT (SPF/DKIM), CNAME de e-mail | | | **não tocar** |

Se o CDN da Hostinger estiver ligado no site, desligue antes (ele recria os registros A).

Os registros atuais têm TTL de 60 s, então a troca pega em minutos. Confira:

```bash
nslookup gwmix.ind.br           # tem que voltar o IP do droplet
docker compose logs -f caddy    # espere "certificate obtained successfully"
```

Abra `https://gwmix.ind.br` e teste páginas, formulários e o painel `/wp-admin`.

**Se algo der errado:** volte o registro A para os IPs antigos (`145.223.124.1` e `147.79.79.78`) e o site volta para a Hostinger.
Mantenha a hospedagem ativa por pelo menos 7 dias depois da troca.

## 6. Depois de migrar (dentro do /wp-admin)

- **Formulários de contato não enviam e-mail no Docker.** Instale o plugin **WP Mail SMTP** e configure com uma caixa do cliente:
  `smtp.hostinger.com`, porta `465`, SSL, usuário e senha da caixa.
- Desative plugins da Hostinger que não servem fora dela (`Hostinger Tools`, `LiteSpeed Cache`).
- Configurações → Links permanentes → **Salvar** (regenera o `.htaccess`).
- Rode `bash backup.sh` e confirme que gerou `wordpress.sql.gz` e `wordpress-files.tgz`.
