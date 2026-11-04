# FCStudio · Home no Elementor

Site da FCStudio (Strategic UI/UX Design, para empresas em geral), montado no Elementor com os 7 breakpoints ativos.
Testada em WordPress 7.1.4 + Elementor 4.3.5 + Pro Elements 4.3.2.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `fcstudio-setup.zip` | **Plugin de um clique** (v1.4): breakpoints, largura útil, cores e fontes, cabeçalho e rodapé globais, as 5 páginas e o menu |
| `paginas/*.json` | Home, Serviços, Planos, Portfólio, Contato, Cabeçalho e Rodapé (formato de modelo do Elementor) |
| `kit-settings.json` | Configurações globais (breakpoints, largura útil, cores, tipografias) |
| `gerar.py` + `sync.sh` | Gerador. Depois de mudar textos ou medidas, rode `./sync.sh` para refazer os JSON e o zip do plugin |
| `prints/` | Capturas das páginas |

## Estrutura do site

- **Cabeçalho e Rodapé** ficam em Elementor > Modelos > Theme Builder e valem para o site todo. Editou ali, muda em todas as páginas.
- As páginas usam o layout **Elementor Largura total** (com cabeçalho e rodapé do Theme Builder).
- Menu principal: Serviços, Planos, Portfólio, Contato. O logo leva para a Home.
- Contato: formulário do Pro com aceite de LGPD, salva em Elementor > Envios e manda e-mail para contato@fcstudio.com.br. **No XAMPP o e-mail não sai** (não há servidor de e-mail); na hospedagem, configure um SMTP (ex.: plugin WP Mail SMTP).

## Requisitos no XAMPP

1. **WordPress 7.1 ou superior.** O Pro Elements 4.3.2 não carrega em versão anterior: o menu hambúrguer some sem aviso no site.
2. Elementor 4.3.5 e Pro Elements 4.3.2 ativos.
3. Tema Hello Elementor ativo. O cabeçalho e o rodapé do Theme Builder substituem os do tema.

## Jeito mais fácil: plugin FCStudio Setup (1 minuto)

1. **Plugins > Adicionar novo > Enviar plugin**, envie `fcstudio-setup.zip` e ative.
2. Vá em **Ferramentas > FCStudio Setup** e clique em **Configurar agora**.
3. Ele ativa os 7 breakpoints, aplica largura útil, cores e fontes, cria cabeçalho e rodapé globais, cria/atualiza as 5 páginas, monta o Menu principal e define a Home como página inicial estática. Pode rodar de novo quando sair versão nova: ele atualiza sem duplicar.
4. Depois, desative e apague o plugin. Ele não é necessário para o site funcionar.

## Breakpoints e largura útil

| Breakpoint | Faixa | Largura útil do conteúdo | Unidade das medidas |
|---|---|---|---|
| Widescreen | a partir de 2400px | 1320px | px |
| Desktop | 1367 a 2399px | 1140px | px |
| Laptop | 1201 a 1366px | 1140px | px |
| Tablet paisagem | 1025 a 1200px | 100% com respiro lateral de 32px | px |
| Tablet retrato | 881 a 1024px | 100% com respiro lateral de 40px | px |
| Celular paisagem | 576 a 880px | 100% com respiro lateral em vw | **vw** (base 740px) |
| Celular retrato | até 575px | 100% com respiro lateral em vw | **vw** (base 390px) |

Os containers internos usam largura 100% e o respiro lateral vem do padding da seção, então nenhum conteúdo encosta na borda e não existe rolagem lateral em nenhuma largura (testado).

No celular paisagem e no celular retrato **todas** as medidas estão em vw: fontes, paddings, margens, gaps, raios, larguras, alturas mínimas, ícones e o logo. Altura de linha e espaçamento entre letras ficam em em, que já acompanham a fonte.
Conversão usada: `vw = px ÷ 7,40` (paisagem) e `vw = px ÷ 3,90` (retrato). Exemplo: texto de 15px no retrato vira 3,846vw.

**Por que o celular retrato vai só até 575px (o padrão do Elementor é 767):** com tudo em vw, um celular deitado de 667px (iPhone SE) caía na regra do retrato e o texto chegava a 26px. Com 575px, todo celular deitado usa a regra da paisagem. Tamanho do texto corrido testado: 15,7px em 360px, 17px em 390px, 15,3px em 667px e 20px em 880px.

**Não volte o breakpoint do celular para 767** em Configurações do site > Breakpoints: as medidas em vw foram calculadas para esta faixa.

## Provisórios para trocar antes de entregar

- E-mail e Instagram no rodapé e no Contato (o WhatsApp já é o real: (11) 91675-1926).
- Fontes servidas do próprio servidor (wp-content/uploads/fcstudio-fonts): Morganite ExtraBold nos títulos e Montserrat 400 a 800 no texto. O Google Fonts fica desligado (site mais rápido e sem enviar dados de visitantes ao Google, LGPD).
- Morganite é freeware para uso comercial, mas a licença proíbe modificar o arquivo: por isso ela vai em TTF original, sem converter nem cortar. A licença está em `fonts/Morganite-License.pdf`.
- **Quem somos**: o logo com brilho verde ocupa o lugar da foto. Quando a foto chegar, troque o widget "Foto (provisório: logo)" por uma imagem com fundo transparente (PNG recortado).
- Portfólio: GWmix tem print real. Sistema de agendamento e landing pages estão sem link e sem imagem: mande os endereços.
- Política de Privacidade: o formulário pede aceite, então a página precisa existir e estar publicada (Configurações > Privacidade).
- Visual: tema dos slides de proposta. Fundo preto com estrelas (`ui/estrelas.jpg`, gerado, sem imagem de terceiros), verde neon #00D61A com gradiente #00E600 a #00B100, títulos condensados em caixa alta, barrinha verde antes dos títulos, traço e linha vertical com ponto. A seção "Como funciona" é clara, com círculos, como o slide de escopo.
- Texto em verde dentro de um título: no Elementor, escreva `<span class="fc-verde">palavras</span>` no campo do título.
