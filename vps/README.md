# VPS FC Studio (DigitalOcean + Docker)

Tudo numa VPS só, cada app no seu container, com HTTPS automático:

| App | Domínio (exemplo) | Container |
|---|---|---|
| n8n (automações) | `n8n.seudominio.com.br` | `n8n` + `postgres` |
| Agenda Clínica Vitalle | `agenda.clinicavitalle.com.br` | servida pelo `caddy` |
| Site WordPress (opcional) | `seudominio.com.br` | `wordpress` + `mariadb` |

Fluxo: Internet → Domínio → Caddy (HTTPS) → app certa.

Baseado na aula "Instalação profissional na VPS com isolamento através de containers do Docker" (Caddy + n8n + PostgreSQL), com duas correções:
- Não instala o `docker.io` antes do Docker oficial (os dois brigam; o script remove o antigo).
- A variável do webhook do n8n é `WEBHOOK_URL`. Com `N8N_WEBHOOK_URL` os webhooks saem com endereço errado.

---

## Passo a passo (tudo pelo terminal do VS Code)

### 1. Criar o droplet (no painel da DigitalOcean)

- **Create → Droplets**
- Região: **New York (NYC1 ou NYC3)**, a mais próxima do Brasil
- Imagem: **Ubuntu 24.04 LTS x64**
- Plano: **Basic → Regular → 2 vCPU / 4 GB RAM** (US$ 24/mês). Com WordPress junto, 2 GB fica no limite.
- Autenticação: **SSH Key** (veja o passo 2 antes) ou senha forte
- Marque **Backups** (semanal) se for hospedar site de cliente
- Hostname: `fcstudio-vps`

Anote o **IP** do droplet.

### 2. Chave SSH (uma vez só, no terminal do VS Code, no seu computador)

```bash
ssh-keygen -t ed25519 -C "fcstudio-vps"     # Enter em tudo
cat ~/.ssh/id_ed25519.pub                    # copie e cole no painel da DO (New SSH Key)
```

No Windows (PowerShell do VS Code) os mesmos comandos funcionam; o arquivo fica em `C:\Users\SEU_USUARIO\.ssh\id_ed25519.pub`.

### 3. Apontar o DNS (onde o domínio está registrado: Registro.br, Hostinger, Cloudflare...)

Crie um **registro A** para cada domínio, apontando para o IP do droplet:

```
n8n      A   IP_DO_DROPLET
agenda   A   IP_DO_DROPLET     (ou no domínio do cliente)
@        A   IP_DO_DROPLET     (só se for usar o WordPress no domínio raiz)
```

Na Cloudflare, deixe a nuvem **cinza** (DNS only), senão o HTTPS não é emitido.
Confira se propagou: `nslookup n8n.seudominio.com.br` tem que devolver o IP do droplet.

### 4. Entrar na VPS

```bash
ssh root@IP_DO_DROPLET
```

### 5. Baixar este repositório e instalar

```bash
git clone https://github.com/fabyawsrestart/fcstudio.git /opt/fcstudio
cd /opt/fcstudio/vps
bash instalar-vps.sh
```

Se o repositório for privado, o `git` pede usuário e senha: use seu usuário do GitHub e, como senha, um **token**
(GitHub → Settings → Developer settings → Personal access tokens → Fine-grained, acesso só de leitura aos dois repositórios).

O script faz sozinho: atualiza o Ubuntu, instala Docker oficial, liga o firewall (só 22, 80 e 443), cria swap,
pergunta os domínios, gera as senhas, baixa a agenda, sobe os containers e testa o HTTPS de cada domínio.

### 6. Primeiro acesso (faça logo em seguida)

- Abra `https://n8n.seudominio.com.br` e **crie a conta de dono na hora**. Quem abrir primeiro vira admin.
- Se ativou o WordPress, abra o domínio do site e conclua a instalação. Depois envie `elementor.4.3.5.zip`
  e `pro-elements.zip` em Plugins → Adicionar novo → Enviar plugin (limite de upload já está em 128 MB).

---

## Dia a dia

```bash
cd /opt/fcstudio/vps
docker compose ps                    # o que está rodando
docker compose logs -f caddy         # logs do proxy / HTTPS (Ctrl+C sai)
docker compose logs -f n8n
bash atualizar.sh                    # backup + atualiza agenda, n8n, Caddy, WordPress
bash backup.sh                       # backup manual em /opt/backups (guarda os 7 últimos)
```

Backup automático todo dia às 3h:

```bash
(crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/fcstudio/vps && bash backup.sh >> /var/log/fcstudio-backup.log 2>&1") | crontab -
```

O backup fica no mesmo servidor. Se o droplet morrer, vai junto. Para site de cliente, ative também o Backups da DigitalOcean
ou copie `/opt/backups` para fora de vez em quando:

```bash
scp -r root@IP_DO_DROPLET:/opt/backups ./backups-vps     # rodar no seu computador
```

### Mudar ou adicionar domínio

```bash
cd /opt/fcstudio/vps
nano .env                 # edite DOMAIN_N8N / DOMAIN_AGENDA / DOMAIN_SITE
bash instalar-vps.sh      # reaplica sem apagar dados nem senhas
```

### Editar arquivos da VPS direto no VS Code

Instale a extensão **Remote - SSH**, `F1 → Remote-SSH: Connect to Host → root@IP_DO_DROPLET` e abra `/opt/fcstudio/vps`.
O terminal integrado já abre dentro da VPS.

---

## Créditos e custos

Os US$ 200 do link de indicação valem por **60 dias**. Depois disso a cobrança no cartão começa sozinha
(o droplet de 2 vCPU / 4 GB custa ~US$ 24/mês + 20% se ativar Backups). Coloque um lembrete para o dia 55.

## Migrar um site existente

Passo a passo do gwmix.ind.br (Hostinger → VPS, sem derrubar o e-mail): [MIGRAR-GWMIX.md](MIGRAR-GWMIX.md)

## Arquivos

- `compose.yaml` — todos os serviços
- `caddy/Caddyfile` — proxy; os sites são gerados em `caddy/sites/` pelo instalador
- `wordpress/uploads.ini` — limites de upload do PHP
- `instalar-vps.sh`, `atualizar.sh`, `backup.sh`
- `.env` — domínios e senhas (gerado na VPS, nunca vai para o GitHub)
