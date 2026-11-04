# FCStudio · Home no Elementor

Home do site da FCStudio (público: dentistas), montada no Elementor com os 7 breakpoints ativos.
Testada em WordPress 7.1.4 + Elementor 4.3.5 + Pro Elements 4.3.2.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `fcstudio-kit.zip` | **Kit completo para importar**: breakpoints, largura útil, cores e tipografias globais, página Home e menu principal |
| `fcstudio-home.json` | Só a página, para importar em Modelos > Importar (se não quiser usar o kit) |
| `kit-settings.json` | Configurações globais em JSON (referência) |
| `gerar.py` | Gerador dos dois JSON. Rode `python3 gerar.py` depois de mudar textos ou medidas |
| `prints/` | Capturas nas 7 resoluções |

## Requisitos no XAMPP

1. **WordPress 7.1 ou superior.** O Pro Elements 4.3.2 não carrega em versão anterior: o menu hambúrguer some sem aviso no site.
2. Elementor 4.3.5 e Pro Elements 4.3.2 ativos.
3. Tema Hello Elementor (recomendado). A página usa o modelo Elementor Canvas, então o tema não interfere no layout.

## Como importar (3 minutos)

1. WP Admin > **Elementor > Ferramentas > Importar/Exportar Kit > Importar**.
2. Envie `fcstudio-kit.zip`, marque tudo (Configurações do site, Conteúdo, Modelos) e confirme.
3. Confira em **Elementor > Configurações do site > Layout > Breakpoints** se os 7 aparecem.
4. Em **Configurações > Leitura**, a Home já vem como página inicial. Confira.
5. Troque os provisórios (lista abaixo) e publique.

## Breakpoints e largura útil

| Breakpoint | Faixa | Largura útil do conteúdo | Unidade das medidas |
|---|---|---|---|
| Widescreen | a partir de 2400px | 1320px | px |
| Desktop | 1367 a 2399px | 1140px | px |
| Laptop | 1201 a 1366px | 1140px | px |
| Tablet paisagem | 1025 a 1200px | 100% com respiro lateral de 32px | px |
| Tablet retrato | 881 a 1024px | 100% com respiro lateral de 40px | px |
| Celular paisagem | 768 a 880px | 100% com respiro lateral em vw | **vw** (base 844px) |
| Celular retrato | até 767px | 100% com respiro lateral em vw | **vw** (base 390px) |

Os containers internos usam largura 100% e o respiro lateral vem do padding da seção, então nenhum conteúdo encosta na borda e não existe rolagem lateral em nenhuma largura (testado).

No celular paisagem e no celular retrato **todas** as medidas estão em vw: fontes, paddings, margens, gaps, raios, larguras, alturas mínimas, ícones e o logo. Altura de linha e espaçamento entre letras ficam em em, que já acompanham a fonte.
Conversão usada: `vw = px ÷ 8,44` (paisagem) e `vw = px ÷ 3,90` (retrato). Exemplo: texto de 15px no retrato vira 3,846vw.

## Provisórios para trocar antes de entregar

- Link do WhatsApp `https://wa.me/5500000000000` (botões e botão flutuante).
- Fonte de títulos: Anton está no lugar da Morganite. Envie a Morganite em **Elementor > Fontes personalizadas** e troque em Configurações do site > Tipografia > "Display".
- Caixas verde-claro do hero e do portfólio: trocar por fotos reais.
- Cores: provisórias, a paleta final ainda vai ser escolhida.
