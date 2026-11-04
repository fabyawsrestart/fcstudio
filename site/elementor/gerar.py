#!/usr/bin/env python3
"""Gera o kit Elementor da FCStudio (site settings + Home) em JSON.

Regras de medida:
- Desktop, widescreen, laptop, tablet paisagem e tablet retrato: px.
- Celular paisagem (mobile_extra, 576-880): vw, base 740 px  -> vw = px / 7.40
- Celular retrato (mobile, ate 575): vw, base 390 px         -> vw = px / 3.90
Line-height em "em" (proporcional a fonte, que ja esta em vw).
"""
import json, os, random

random.seed(7)
OUT = os.path.dirname(os.path.abspath(__file__))
BASE_L, BASE_M = 7.40, 3.90

def uid():
    return '%07x' % random.getrandbits(28)

def vw(px, base):
    return round(px / base, 3)

# ---------- medidas responsivas ----------
def slider(key, d, t=None, l=None, m=None, lap=None, te=None, ws=None):
    """d/t/lap/te/ws em px; l (paisagem @844) e m (retrato @390) em px convertidos para vw."""
    t = d if t is None else t
    l = t if l is None else l
    m = l if m is None else m
    s = {key: {'unit': 'px', 'size': d}}
    if lap is not None: s[key + '_laptop'] = {'unit': 'px', 'size': lap}
    if te is not None: s[key + '_tablet_extra'] = {'unit': 'px', 'size': te}
    if ws is not None: s[key + '_widescreen'] = {'unit': 'px', 'size': ws}
    s[key + '_tablet'] = {'unit': 'px', 'size': t}
    s[key + '_mobile_extra'] = {'unit': 'vw', 'size': vw(l, BASE_L)}
    s[key + '_mobile'] = {'unit': 'vw', 'size': vw(m, BASE_M)}
    return s

def dims(key, d, t=None, l=None, m=None, te=None):
    """Cada valor e (top, right, bottom, left) em px."""
    def mk(v, unit, base=None):
        v = [vw(x, base) if base else x for x in v]
        return {'unit': unit, 'top': str(v[0]), 'right': str(v[1]), 'bottom': str(v[2]), 'left': str(v[3]), 'isLinked': False}
    t = d if t is None else t
    l = t if l is None else l
    m = l if m is None else m
    s = {key: mk(d, 'px'), key + '_tablet': mk(t, 'px'), key + '_mobile_extra': mk(l, 'vw', BASE_L), key + '_mobile': mk(m, 'vw', BASE_M)}
    if te is not None: s[key + '_tablet_extra'] = mk(te, 'px')
    return s

def gap(key, d, t=None, l=None, m=None):
    t = d if t is None else t
    l = t if l is None else l
    m = l if m is None else m
    g = lambda v, u: {'unit': u, 'size': v, 'column': str(v), 'row': str(v), 'isLinked': True}
    return {key: g(d, 'px'), key + '_tablet': g(t, 'px'), key + '_mobile_extra': g(vw(l, BASE_L), 'vw'), key + '_mobile': g(vw(m, BASE_M), 'vw')}

def radius(key, d, l=None, m=None):
    l = d if l is None else l
    m = l if m is None else m
    r = lambda v, u: {'unit': u, 'top': str(v), 'right': str(v), 'bottom': str(v), 'left': str(v), 'isLinked': True}
    return {key: r(d, 'px'), key + '_mobile_extra': r(vw(l, BASE_L), 'vw'), key + '_mobile': r(vw(m, BASE_M), 'vw')}

def W(el, d, t=None, l=None, m=None):
    """Largura de container filho em fila: valores em % (ou 'fit' = largura do conteudo)."""
    def u(v):
        return {'unit': 'custom', 'size': 'fit-content'} if v == 'fit' else {'unit': '%', 'size': v}
    t = d if t is None else t
    l = t if l is None else l
    m = l if m is None else m
    st = el['settings']
    st.pop('_flex_size', None)
    if el['elType'] == 'widget':
        # widget em fila: largura personalizada do Elementor (_element_custom_width)
        if d == 'fit':
            st['_element_width'] = 'auto'; st['_flex_size'] = 'none'
            return el
        st['_element_width'] = 'initial'
        for sfx, v in (('', d), ('_tablet', t), ('_mobile_extra', l), ('_mobile', m)):
            st['_element_custom_width' + sfx] = {'unit': '%', 'size': v}
        return el
    st.update({'width': u(d), 'width_tablet': u(t), 'width_mobile_extra': u(l), 'width_mobile': u(m)})
    return el

# ---------- tokens ----------
# Tema dos slides: fundo preto com estrelas e verde neon (gradiente #00E600 a #00B100)
COLORS_SYS = [('primary', 'Verde neon', '#00D61A'), ('secondary', 'Branco (títulos)', '#FFFFFF'), ('text', 'Cinza (texto)', '#A3A3A3'), ('accent', 'Verde claro', '#00E600')]
COLORS_CUSTOM = [('verde700', 'Verde 700 (fim do gradiente)', '#00A818'), ('verde100', 'Verde escuro (fundo de ícone)', '#0B2B12'), ('neutro50', 'Preto 2 (seção alternada)', '#0D0D0D'),
                 ('cinza300', 'Cinza claro (texto de apoio)', '#CBD2D9'), ('branco', 'Branco', '#FFFFFF'), ('preto', 'Preto (fundo)', '#050505'), ('card', 'Cartão', '#141414'),
                 ('linha', 'Linha', '#2A2A2A'), ('tinta', 'Tinta (título em fundo claro)', '#0A0A0A'), ('tinta2', 'Tinta 2 (texto em fundo claro)', '#4B5563'),
                 ('verde800', 'Verde em fundo claro', '#007A10'), ('claro', 'Fundo claro', '#F2F2F0')]
C = lambda cid: 'globals/colors?id=' + cid

DISPLAY = 'Morganite'  # títulos condensados em caixa alta, como nos slides (arquivo da Fab, servido localmente)
TEXT = 'Montserrat'
# id, titulo, familia, peso, (D, T, L, M) px, line-height em, letter-spacing em, transform
TYPO = [
    ('fc_h1', 'Título hero (H1)', DISPLAY, '800', (132, 112, 96, 84), 0.9, 0.005, 'uppercase'),
    ('fc_h2', 'Título de seção (H2)', DISPLAY, '800', (96, 84, 72, 64), 0.92, 0.005, 'uppercase'),
    ('fc_num', 'Destaque / preço', DISPLAY, '800', (60, 56, 52, 46), 0.95, 0.01, 'uppercase'),
    ('fc_kicker', 'Chamada (linha de cima)', TEXT, '800', (56, 46, 38, 30), 1.05, 0, 'uppercase'),
    ('fc_h3', 'Título de item (H3)', TEXT, '700', (20, 19, 18, 17), 1.35, 0.02, 'none'),
    ('fc_lead', 'Texto de apoio', TEXT, '400', (19, 18, 17, 16), 1.6, 0.04, 'none'),
    ('fc_body', 'Texto corpo', TEXT, '400', (16, 16, 15, 15), 1.7, 0.03, 'none'),
    ('fc_caption', 'Etiqueta', TEXT, '700', (13, 13, 12, 12), 1.4, 0.18, 'uppercase'),
    ('fc_button', 'Botão', TEXT, '700', (14, 14, 14, 14), 1.0, 0.12, 'uppercase'),
]
T = lambda tid: 'globals/typography?id=' + tid

def typo_preset(tid, title, fam, w, sizes, lh, ls, tr):
    d, t, l, m = sizes
    p = {'_id': tid, 'title': title, 'typography_typography': 'custom', 'typography_font_family': fam, 'typography_font_weight': w,
         'typography_line_height': {'unit': 'em', 'size': lh}, 'typography_letter_spacing': {'unit': 'em', 'size': ls}, 'typography_text_transform': tr}
    p.update(slider('typography_font_size', d, t, l, m, ws=round(d * 1.15)))
    return p

# ---------- elementos ----------
def con(children, **s):
    return {'id': uid(), 'elType': 'container', 'isInner': False, 'settings': s, 'elements': [c for c in children if c]}

def w(kind, **s):
    return {'id': uid(), 'elType': 'widget', 'widgetType': kind, 'settings': s, 'elements': []}

def H(text, tid='fc_h2', color='secondary', tag='h2', align=None, **extra):
    s = {'title': text, 'header_size': tag, '__globals__': {'typography_typography': T(tid), 'title_color': C(color)}}
    if tid == 'fc_h2' and tag == 'h2': s['_css_classes'] = 'fc-barra'  # barrinha verde à esquerda, como nos slides
    if align: s['align'] = align
    s.update(extra)
    return w('heading', **s)

def P(text, tid='fc_body', color='text', **extra):
    s = {'editor': '<p>' + text + '</p>', '__globals__': {'typography_typography': T(tid), 'text_color': C(color)}}
    s.update(slider('paragraph_spacing', 0, l=0, m=0))  # o espaçamento vem do gap do container
    s.update(extra)
    return w('text-editor', **s)

WA = 'https://wa.me/5511916751926?text=Ol%C3%A1%2C%20quero%20saber%20mais%20sobre%20os%20servi%C3%A7os%20da%20FC%20Studio'

def B(text, kind='primary', url=WA, full_mobile=True, **extra):
    bg, fg, border = {'primary': ('primary', 'preto', None), 'secondary': (None, 'primary', 'primary'),
                      'white': ('branco', 'preto', None), 'dark': ('primary', 'preto', None),
                      'light': (None, 'branco', 'branco')}[kind]
    s = {'text': text, 'link': {'url': url, 'is_external': url.startswith('http'), 'nofollow': ''},
         '__globals__': {'typography_typography': T('fc_button'), 'button_text_color': C(fg)}}
    s['background_color'] = '#00000000'
    if bg: s['__globals__']['background_color'] = C(bg)
    if border:
        s.update({'border_border': 'solid', '__globals__': {**s['__globals__'], 'border_color': C(border)}})
        s.update(slider('border_width', 2, l=2, m=2) and {'border_width': {'unit': 'px', 'top': '2', 'right': '2', 'bottom': '2', 'left': '2', 'isLinked': True},
                 'border_width_mobile_extra': {'unit': 'vw', 'top': str(vw(2, BASE_L)), 'right': str(vw(2, BASE_L)), 'bottom': str(vw(2, BASE_L)), 'left': str(vw(2, BASE_L)), 'isLinked': True},
                 'border_width_mobile': {'unit': 'vw', 'top': str(vw(2, BASE_M)), 'right': str(vw(2, BASE_M)), 'bottom': str(vw(2, BASE_M)), 'left': str(vw(2, BASE_M)), 'isLinked': True}})
    s.update(radius('border_radius', 6, 6, 6))
    s.update(dims('text_padding', (20, 32, 20, 32), (18, 28, 18, 28), (17, 26, 17, 26), (18, 22, 18, 22)))
    if full_mobile:
        s['align_mobile'] = 'justify'
    if kind in ('primary', 'dark'): s['_css_classes'] = 'fc-neon'  # gradiente verde dos slides
    s.update(extra)
    return w('button', **s)

def ICON(icon, lib='fa-solid', **extra):
    s = {'selected_icon': {'value': icon, 'library': lib}, 'view': 'stacked', 'shape': 'square', 'align': 'left',
         '__globals__': {'primary_color': C('verde100'), 'secondary_color': C('primary')}}
    s.update(slider('size', 22, l=20, m=20))
    s.update(slider('icon_padding', 13, l=12, m=12))
    s.update(radius('border_radius', 12, 12, 12))
    s.update(extra)
    return w('icon', **s)

def LIST(items, light=False):
    s = {'icon_list': [{'_id': uid(), 'text': t, 'selected_icon': {'value': 'fas fa-check', 'library': 'fa-solid'}} for t in items],
         '__globals__': {'icon_typography_typography': T('fc_body'), 'text_color': C('branco' if light else 'secondary'), 'icon_color': C('accent' if light else 'primary')}}
    s.update(slider('icon_size', 14, l=13, m=13))
    s.update(slider('space_between', 10, l=9, m=9))
    s.update(slider('text_indent', 10, l=9, m=9))
    return w('icon-list', **s)

BG = {'branco': 'preto', 'secondary': 'preto', 'verde100': 'neutro50'}  # mapa do tema claro antigo para o escuro

def section(name, children, bg='neutro50', css_id=None, py=(112, 88, 64, 64), px=(0, 40, 40, 24), gap_=(48, 40, 32, 32), te_px=32, **extra):
    bg = BG.get(bg, bg)
    s = {'_title': name, 'content_width': 'boxed', 'flex_direction': 'column', 'background_background': 'classic', '__globals__': {'background_color': C(bg)}}
    s.update(dims('padding', (py[0], px[0], py[0], px[0]), (py[1], px[1], py[1], px[1]), (py[2], px[2], py[2], px[2]), (py[3], px[3], py[3], px[3]), te=(py[0], te_px, py[0], te_px)))
    s.update(gap('flex_gap', *gap_))
    if css_id: s['_element_id'] = css_id
    s.update(extra)
    # sem o "lazy load" de fundo do Elementor: ele apaga gradientes e estrelas até a seção entrar na tela
    s['css_classes'] = (s.get('css_classes', '') + ' e-no-lazyload').strip()
    return con(children, **s)

def col(children, name=None, gap_=(16, 16, 14, 14), **extra):
    s = {'content_width': 'full', 'flex_direction': 'column'}
    if name: s['_title'] = name
    s.update(gap('flex_gap', *gap_))
    s.update(dims('padding', (0, 0, 0, 0)))
    s.update(extra)
    return con(children, **s)

def row(children, name=None, gap_=(24, 24, 20, 16), mobile_dir='column', landscape_dir='column', tablet_dir='row', **extra):
    s = {'content_width': 'full', 'flex_direction': 'row', 'flex_direction_tablet': tablet_dir, 'flex_direction_mobile_extra': landscape_dir, 'flex_direction_mobile': mobile_dir,
         'flex_wrap': 'nowrap'}
    if name: s['_title'] = name
    s.update(gap('flex_gap', *gap_))
    s.update(dims('padding', (0, 0, 0, 0)))
    s.update(extra)
    return con(children, **s)

def grid(children, cols=(3, 3, 2, 1), name=None, gap_=(24, 24, 20, 16)):
    d, t, l, m = cols
    s = {'container_type': 'grid', 'content_width': 'full',
         'grid_columns_grid': {'unit': 'fr', 'size': d}, 'grid_columns_grid_tablet': {'unit': 'fr', 'size': t},
         'grid_columns_grid_mobile_extra': {'unit': 'fr', 'size': l}, 'grid_columns_grid_mobile': {'unit': 'fr', 'size': m},
         'grid_rows_grid': {'unit': 'fr', 'size': 1}, 'grid_auto_flow': 'row'}
    if name: s['_title'] = name
    g = lambda v, u: {'unit': u, 'size': v, 'column': str(v), 'row': str(v), 'isLinked': True}
    s.update({'grid_gaps': g(gap_[0], 'px'), 'grid_gaps_tablet': g(gap_[1], 'px'), 'grid_gaps_mobile_extra': g(vw(gap_[2], BASE_L), 'vw'), 'grid_gaps_mobile': g(vw(gap_[3], BASE_M), 'vw')})
    s.update(dims('padding', (0, 0, 0, 0)))
    return con(children, **s)

def card(children, bg='card', pad=(32, 28, 24, 24), gap_=(12, 12, 10, 10), r=8, **extra):
    s = {'content_width': 'full', 'flex_direction': 'column', 'background_background': 'classic', '__globals__': {'background_color': C(bg)}}
    s.update(dims('padding', (pad[0],) * 4, (pad[1],) * 4, (pad[2],) * 4, (pad[3],) * 4))
    s.update(gap('flex_gap', *gap_))
    s.update(radius('border_radius', r, r - 2, r - 2))
    s.update(extra)
    return con(children, **s)

def line_row(children, name=None, gap_=(48, 32, 24, 12), top=True, **extra):
    """Linha de lista editorial: separador fino em cima, sem cartão."""
    r = row(children, name=name, gap_=gap_, **extra)
    r['settings'].update({'border_border': 'solid', 'border_width': {'unit': 'px', 'top': '1' if top else '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False},
                          '__globals__': {**r['settings'].get('__globals__', {}), 'border_color': C('linha')}})
    r['settings'].update(dims('padding', (28, 0, 28, 0), (24, 0, 24, 0), (20, 0, 20, 0), (20, 0, 20, 0)))
    r['settings']['border_width_mobile_extra'] = {'unit': 'vw', 'top': str(vw(1, BASE_L)) if top else '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False}
    r['settings']['border_width_mobile'] = {'unit': 'vw', 'top': str(vw(1, BASE_M)) if top else '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False}
    return r

def IMG(token, alt, r=14, shadow='cinza'):
    s = {'image': {'url': 'fc-img://' + token, 'id': 'fc-imgid://' + token, 'alt': alt}, 'image_size': 'full', '_title': 'Imagem ' + token}
    s.update(slider('width', 100, l=100, m=100)); s['width'] = {'unit': '%', 'size': 100}
    for k in ('width_tablet', 'width_mobile_extra', 'width_mobile'): s[k] = {'unit': '%', 'size': 100}
    s.update(radius('image_border_radius', r, r - 2, r - 4))
    s['_css_classes'] = 'fc-offset ' + ('fc-offset--verde' if shadow == 'verde' else 'fc-offset--cinza')
    return w('image', **s)

def eyebrow(text, light=False):
    # Sem sobretítulo: o título fala sozinho (referência impeccable). Mantido para não quebrar chamadas.
    return None

def logo_svg(color_sym, color_word):
    here = os.path.join(OUT, '..', '..', 'marca', 'logo', 'logo-fcstudio-verde.svg')
    svg = open(here).read().strip()
    svg = svg.replace('width="240" height="168" ', 'style="display:block;width:100%;height:auto" ')
    svg = svg.replace('fill="#168A5B"', 'fill="' + color_sym + '"').replace('fill="#1F2933"', 'fill="' + color_word + '"')
    return svg

def LOGO(width_d=64, light=False, l=56, m=50):
    s = {'html': logo_svg('#00D61A', '#FFFFFF'), '_element_width': 'initial'}  # site todo é escuro
    s.update(slider('_element_custom_width', width_d, l=l, m=m))
    s['_title'] = 'Logo FC Studio'
    return w('html', **s)

# ---------- página ----------
def header():
    # Menu do Pro Elements: horizontal no desktop/laptop/tablet paisagem, hambúrguer a partir do tablet retrato
    nav = w('nav-menu', menu='menu-principal', layout='horizontal', pointer='none', dropdown='tablet', toggle='burger', full_width='stretch', toggle_align='right', align_items='right',
            text_align='aside', _title='Menu',
            __globals__={'menu_typography_typography': T('fc_button'), 'color_menu_item': C('secondary'), 'color_menu_item_hover': C('primary'),
                         'dropdown_typography_typography': T('fc_button'), 'color_dropdown_item': C('secondary'), 'background_color_dropdown_item': C('card'),
                         'color_dropdown_item_hover': C('preto'), 'background_color_dropdown_item_hover': C('primary'), 'toggle_color': C('secondary'), 'toggle_background_color': C('verde100')},
            **slider('padding_horizontal_menu_item', 16, 14, 14, 14), **slider('toggle_size', 22, 22, 24, 24), **slider('toggle_border_width', 0, 0, 0, 0),
            **radius('toggle_border_radius', 10, 10, 10), **slider('dropdown_top_distance', 12, 12, 12, 12),
            **slider('padding_horizontal_dropdown_item', 40, 40, 40, 24), **slider('padding_vertical_dropdown_item', 14, 14, 14, 14))
    cta = B('Orçamento', 'primary', U('orcamento'), full_mobile=False, hide_mobile='hidden-mobile', hide_mobile_extra='hidden-mobile_extra')
    s = {'_title': 'Cabeçalho', 'content_width': 'boxed', 'flex_direction': 'row', 'flex_direction_mobile': 'row', 'flex_direction_mobile_extra': 'row', 'flex_direction_tablet': 'row',
         'flex_justify_content': 'space-between', 'flex_align_items': 'center', 'flex_wrap': 'nowrap',
         'background_background': 'classic', '__globals__': {'background_color': C('preto'), 'border_color': C('linha')}, 'z_index': 100,
         'border_border': 'solid', 'border_width': {'unit': 'px', 'top': '0', 'right': '0', 'bottom': '1', 'left': '0', 'isLinked': False},
         'border_width_mobile_extra': {'unit': 'vw', 'top': '0', 'right': '0', 'bottom': str(vw(1, BASE_L)), 'left': '0', 'isLinked': False},
         'border_width_mobile': {'unit': 'vw', 'top': '0', 'right': '0', 'bottom': str(vw(1, BASE_M)), 'left': '0', 'isLinked': False}}
    s.update(dims('padding', (16, 0, 16, 0), (14, 40, 14, 40), (12, 40, 12, 40), (12, 24, 12, 24), te=(16, 32, 16, 32)))
    s.update(gap('flex_gap', 24, 16, 16, 12))
    right = row([nav, cta], name='Direita', gap_=(32, 16, 12, 12), mobile_dir='row', landscape_dir='row', flex_align_items='center', flex_justify_content='flex-end')
    W(right, 'fit')
    lg = LOGO(64, l=60, m=52); lg['settings']['html'] = '<a href="fc://home" aria-label="FC Studio, página inicial" style="display:block">' + lg['settings']['html'] + '</a>'
    return con([lg, right], **s)

def hero():
    buttons = row([B('Solicite um orçamento', 'primary', U('orcamento')), B('Ver planos', 'light', U('planos'))], name='Botões', gap_=(12, 12, 12, 10), landscape_dir='row', mobile_dir='column')
    text = col([H('Strategic UI/UX Design', 'fc_caption', 'primary', 'p'),
                H('Sites que trazem <span class="fc-verde">novos clientes</span> para o seu negócio', 'fc_h1', 'secondary', 'h1'),
                P('Seu cliente encontra você no Google, confia no que vê e chama no WhatsApp. A FC Studio cuida do site, do chatbot, dos anúncios e dos vídeos.', 'fc_lead', 'cinza300'),
                buttons, P('Site no ar em 15 dias &nbsp;·&nbsp; Suporte por 3 meses', 'fc_body', 'text')],
               name='Texto', gap_=(28, 24, 22, 20))
    proof = col([IMG('gwmix', 'Site da GWmix feito pela FC Studio', shadow='verde'),
                 P('Último projeto entregue: <a href="https://gwmix.ind.br" target="_blank" rel="noopener" style="color:#fff;text-decoration:underline;text-underline-offset:.2em">gwmix.ind.br</a>', 'fc_body', 'cinza300')],
                name='Prova: projeto real', gap_=(28, 24, 22, 20))
    W(text, 56, 100); W(proof, 44, 100)
    r_ = row([text, proof], name='Hero · conteúdo', gap_=(72, 56, 40, 44), tablet_dir='column', flex_align_items='center')
    return section('Hero', [r_], 'preto', 'inicio', py=(112, 80, 56, 48), css_classes='fc-estrelas')

def beneficios():
    items = [('Aparece no Google', 'Site rápido e preparado para as buscas da sua região e do seu segmento.'),
             ('Passa confiança', 'Design profissional, fotos reais e informação clara, sem enrolação.'),
             ('Vira contato', 'WhatsApp, formulário e chatbot prontos para atender na hora em que o cliente decide.')]
    rows = []
    for i, (t, d) in enumerate(items):
        a = H(t, 'fc_h3', 'secondary', 'h3'); b = P(d)
        r = line_row([a, b], name=t, landscape_dir='row', mobile_dir='column', gap_=(32, 24, 20, 6))
        W(a, 40, 40, 40, 100); W(b, 60, 60, 60, 100)
        rows.append(r)
    head = col([H('O cliente pesquisa antes de comprar'),
                P('Antes de ligar ou visitar, ele procura sua empresa no Google e compara. Um site bem feito é o que faz ele escolher você.', 'fc_lead')], name='Título da seção', gap_=(20, 18, 16, 14))
    lst = col(rows, 'Lista', gap_=(0, 0, 0, 0))
    W(head, 42, 100, 100, 100); W(lst, 58, 100, 100, 100)
    return section('Benefícios', [row([head, lst], name='Benefícios · conteúdo', gap_=(80, 40, 32, 28), tablet_dir='column')], 'branco')

def servicos():
    items = [(t, d) for _, t, d, _ in SERVICOS]
    rows = []
    for t, d in items:
        a = H(t, 'fc_h2', 'secondary', 'h3'); b = P(d, 'fc_lead')
        a['settings']['__globals__']['typography_typography'] = T('fc_num')
        r = line_row([a, b], name=t, landscape_dir='row', mobile_dir='column', gap_=(48, 32, 24, 8), flex_align_items='center')
        W(a, 50, 50, 50, 100); W(b, 50, 50, 50, 100)
        rows.append(r)
    head = row([H('Tudo o que seu negócio precisa para vender mais online'), B('Ver os serviços', 'secondary', U('servicos'), full_mobile=False)],
               name='Título da seção', gap_=(32, 24, 20, 20), tablet_dir='row', landscape_dir='column', mobile_dir='column', flex_align_items='flex-end', flex_align_items_mobile='flex-start', flex_align_items_mobile_extra='flex-start', flex_justify_content='space-between')
    W(head['elements'][0], 70, 70, 100, 100); W(head['elements'][1], 'fit')
    return section('Serviços', [head, col(rows, 'Lista de serviços', gap_=(0, 0, 0, 0))], 'neutro50', 'servicos')

LIGHT = {C('secondary'): C('tinta'), C('text'): C('tinta2'), C('primary'): C('verde800'), C('cinza300'): C('tinta2')}

def lighten(els):
    for e in els:
        g = e['settings'].get('__globals__', {})
        for k, v in list(g.items()):
            if k != 'background_color' and v in LIGHT: g[k] = LIGHT[v]
        lighten(e['elements'])
    return els

def como_funciona():
    steps = []
    for n, t, d in [('1', 'Conversa', '30 minutos por vídeo para entender seu negócio e seus clientes.'),
                    ('2', 'Layout para aprovar', 'Você vê o site pronto antes de qualquer código.'),
                    ('3', 'Site no ar', 'Publicamos com domínio, SSL e WhatsApp configurados.'),
                    ('4', 'Acompanhamento', '3 meses de suporte e ajustes sem custo extra.')]:
        c = col([H(n, 'fc_h1', 'primary', 'span'), H(t, 'fc_h3', 'secondary', 'h3'), P(d)], gap_=(10, 10, 8, 8))
        c['settings'].update({'border_border': 'solid', 'border_width': {'unit': 'px', 'top': '2', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False},
                              'border_width_mobile_extra': {'unit': 'vw', 'top': str(vw(2, BASE_L)), 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False},
                              'border_width_mobile': {'unit': 'vw', 'top': str(vw(2, BASE_M)), 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False},
                              '__globals__': {'border_color': C('primary')}})
        c['settings'].update(dims('padding', (20, 0, 0, 0), (18, 0, 0, 0), (16, 0, 0, 0), (16, 0, 0, 0)))
        steps.append(c)
    head = col([H('Do primeiro contato ao site no ar em 15 dias')], name='Título da seção')
    sec = section('Como funciona', [head, grid(steps, (4, 2, 2, 1), 'Passos', gap_=(32, 32, 24, 32))], 'claro', 'como-funciona', css_classes='fc-claro fc-circulos')
    lighten(sec['elements'])
    return sec

def planos():
    data = [('Essencial', 'Landing page', 'R$ 1.490', 'pagamento único', ['1 página focada em uma oferta', 'Botão de WhatsApp em todas as telas', 'Domínio e SSL configurados', 'Entrega em 10 dias'], False),
            ('Empresa', 'Site completo', 'R$ 2.990', 'pagamento único', ['Até 6 páginas', 'Google Meu Negócio otimizado', 'Página para cada produto ou serviço', '3 meses de suporte'], True),
            ('Crescimento', 'Site + marketing', 'R$ 1.290', 'por mês + implantação do site', ['Tudo do plano Empresa', 'Anúncios no Google e Instagram', '4 vídeos editados por mês', 'Relatório mensal de resultados'], False)]
    cards = []
    for nm, sub, price, per, items, hi in data:
        kids = []
        if hi:
            kids.append(H('Mais escolhido', 'fc_caption', 'secondary', 'p', _element_width='auto', _flex_align_self='flex-start', _background_background='classic',
                          **dims('_padding', (6, 12, 6, 12), (6, 12, 6, 12), (5, 10, 5, 10), (5, 10, 5, 10)), **radius('_border_radius', 999, 999, 999),
                          **{'__globals__': {'typography_typography': T('fc_caption'), 'title_color': C('preto'), '_background_color': C('accent')}}))
        kids += [H(nm, 'fc_h3', 'branco' if hi else 'secondary', 'h3'), P(sub, 'fc_body', 'cinza300' if hi else 'text'),
                 H(price, 'fc_num', 'branco' if hi else 'primary', 'p'), H(per, 'fc_caption', 'cinza300' if hi else 'text', 'p'),
                 LIST(items, hi), B('Quero este plano', 'primary' if hi else 'secondary', full_mobile=True, align='justify')]
        c = card(kids, bg='card', gap_=(16, 14, 14, 14), _title='Plano ' + nm, css_classes='fc-offset fc-offset--verde' if hi else 'fc-borda')
        if hi:
            c['settings']['_flex_order_mobile'] = 'start'
        cards.append(c)
    head = col([eyebrow('Planos'), H('Escolha o plano do seu negócio'), P('Pagamento em até 10x. Sem fidelidade nos planos mensais.', 'fc_lead')], name='Título da seção')
    plans_row = row(cards, name='Cards de plano', gap_=(24, 16, 20, 16), tablet_dir='row', flex_align_items='stretch')
    for c in cards:
        W(c, 33.333, 33.333, 100, 100)
    # no celular o plano em destaque vem primeiro
    cards[1]['settings']['_flex_order_mobile'] = 'start'
    cards[1]['settings']['_flex_order_mobile_extra'] = 'start'
    return section('Planos', [head, plans_row], 'neutro50', 'planos')

def portfolio():
    img = IMG('gwmix', 'Site da GWmix feito pela FC Studio')
    txt = col([H('GWmix', 'fc_num', 'secondary', 'h3'),
               P('Site institucional e de vendas para fabricante de bombas, misturadores e aditivos para argamassa na Grande SP. Catálogo de produtos, locação e orçamento pelo WhatsApp.'),
               B('Ver site no ar', 'secondary', 'https://gwmix.ind.br', full_mobile=True)], gap_=(16, 14, 12, 12))
    W(img, 60, 100, 55, 100); W(txt, 40, 100, 45, 100)
    feat = row([img, txt], name='Destaque GWmix', gap_=(56, 32, 28, 24), tablet_dir='column', landscape_dir='row', flex_align_items='center')
    head = row([H('Projetos entregues'), B('Ver portfólio', 'secondary', U('portfolio'), full_mobile=False)], name='Título da seção', gap_=(24, 24, 20, 20),
               tablet_dir='row', landscape_dir='row', mobile_dir='column', flex_align_items='flex-end', flex_align_items_mobile='flex-start', flex_align_items_mobile_extra='flex-start', flex_justify_content='space-between')
    W(head['elements'][1], 'fit')
    return section('Portfólio', [head, feat], 'branco', 'portfolio')

def faq():
    qa = [('Quanto tempo leva para o site ficar pronto?', 'Em média 15 dias depois que você aprova o layout.'),
          ('Vou conseguir editar o site depois?', 'Sim. O site é feito em WordPress com Elementor, e você recebe um vídeo mostrando como trocar textos e fotos.'),
          ('Vocês cuidam da hospedagem e do domínio?', 'Ajudamos a contratar e configuramos tudo. A conta fica no seu nome.'),
          ('Vocês atendem qualquer tipo de negócio?', 'Sim. Comércio, serviços, indústria, saúde e profissionais liberais. O projeto parte do seu cliente, não de um modelo pronto.')]
    return faq_list(qa)

def cta():
    # slide "Você está pronto para o sucesso?": linha vertical com ponto, chamada em duas alturas
    t = H('Você está pronto<br><span class="fc-display fc-verde">para crescer?</span>', 'fc_kicker', 'secondary', 'h2')
    txt = col([t, P('Conversa de 30 minutos, sem compromisso. Você sai com um plano claro para trazer mais clientes. Se preferir, chame direto no '
                    '<a href="https://wa.me/5511916751926" style="color:#00E600;font-weight:700;text-decoration:none;white-space:nowrap">WhatsApp (11) 91675-1926</a>.', 'fc_lead', 'cinza300'),
               B('Solicite um orçamento', 'primary', U('orcamento'))], name='Chamada', gap_=(32, 28, 24, 24), css_classes='fc-linha-v')
    txt['settings'].update(dims('padding', (16, 0, 64, 72), (16, 0, 56, 56), (8, 0, 48, 40), (8, 0, 40, 28)))
    W(txt, 72, 100, 100, 100)
    return section('Chamada final', [txt], 'preto', 'contato', py=(128, 96, 72, 64), css_classes='fc-estrelas')

def footer():
    c1 = col([LOGO(80, True, 70, 64), P('Strategic UI/UX Design. Sites, chatbots, anúncios e vídeos para empresas que querem crescer.', 'fc_body', 'cinza300')], gap_=(16, 16, 14, 14), _flex_size='grow')
    def links(title, items):
        return col([H(title, 'fc_caption', 'primary', 'p')] + [P(i, 'fc_body', 'branco') for i in items], gap_=(10, 10, 8, 8), _flex_size='grow')
    nav_ = links('Navegação', ['<a href="fc://%s" style="color:inherit">%s</a>' % x for x in (('servicos', 'Serviços'), ('planos', 'Planos'), ('portfolio', 'Portfólio'), ('quem-somos', 'Quem Somos'), ('orcamento', 'Orçamento'), ('contato', 'Contato'))])
    cont_ = links('Contato', ['<a href="https://wa.me/5511916751926" style="color:inherit">WhatsApp: (11) 91675-1926</a>', 'contato@fcstudio.com.br', 'Instagram: @fcstudio'])
    W(c1, 40, 40, 40, 100); W(nav_, 30, 30, 30, 100); W(cont_, 30, 30, 30, 100)
    cols_ = row([c1, nav_, cont_], name='Colunas', gap_=(64, 40, 32, 32), landscape_dir='row', mobile_dir='column')
    line = w('divider', **{'__globals__': {'color': C('linha')}, **slider('weight', 1, l=1, m=1)})
    return section('Rodapé', [cols_, line, H('© 2026 FC Studio. Todos os direitos reservados.', 'fc_caption', 'cinza300', 'p')], 'secondary', 'rodape', py=(56, 48, 40, 40), gap_=(32, 28, 24, 24))

def whatsapp_float():
    b = B('WhatsApp', 'primary', full_mobile=False, _position='fixed', _offset_orientation_h='end', _z_index=50,
          hide_desktop='hidden-desktop', hide_laptop='hidden-laptop', hide_widescreen='hidden-widescreen', hide_tablet_extra='hidden-tablet_extra', hide_tablet='hidden-tablet',
          selected_icon={'value': 'fab fa-whatsapp', 'library': 'fa-brands'}, icon_align='left',
          button_box_shadow_box_shadow_type='yes', button_box_shadow_box_shadow={'horizontal': 0, 'vertical': 8, 'blur': 20, 'spread': 0, 'color': 'rgba(0,0,0,0.2)'},
          _element_width='initial', _title='Botão flutuante WhatsApp')
    b['settings'].update(slider('_offset_x_end', 16, l=20, m=16))
    b['settings'].update(slider('_offset_y', 16, l=20, m=16))
    b['settings']['_offset_orientation_v'] = 'end'
    b['settings'].update(slider('_offset_y_end', 16, l=20, m=16))
    return b

def mark_inner(els, depth=0):
    for e in els:
        if e['elType'] == 'container':
            e['isInner'] = depth > 0
        mark_inner(e['elements'], depth + 1)
    return els

# ---------- links internos ----------
# "fc://slug" vira o link real da página quando o plugin FCStudio Setup instala o site
U = lambda slug: 'fc://' + slug

def page_hero(eye, title, lead, buttons=None, name='Topo da página'):
    kids = [eyebrow(eye), H(title, 'fc_h1', 'secondary', 'h1'), P(lead, 'fc_lead')]
    if buttons:
        kids.append(row(buttons, name='Botões', gap_=(12, 12, 12, 10), landscape_dir='row', mobile_dir='column'))
    text = col(kids, name='Texto', gap_=(24, 22, 20, 18))
    W(text, 75, 100, 100, 100)
    return section(name, [text], 'preto', 'inicio', py=(112, 80, 56, 48), css_classes='fc-estrelas')

SERVICOS = [
    ('01', 'Sites para empresas', 'Site institucional completo, rápido e pronto para o Google, com WhatsApp em todas as telas.',
     ['Até 6 páginas com textos escritos para vender', 'Página para cada produto ou serviço', 'Mapa, horários e botão de WhatsApp', 'Google Meu Negócio otimizado']),
    ('02', 'Landing pages', 'Uma página, uma oferta. Feita para transformar clique de anúncio em contato.',
     ['Texto focado em uma única oferta', 'Perguntas frequentes do seu cliente', 'Formulário e WhatsApp no topo', 'Pronta para receber anúncios']),
    ('03', 'Chatbots', 'Atendimento automático no WhatsApp e no site: responde dúvidas, qualifica o contato e passa para você.',
     ['Respostas para as perguntas mais comuns', 'Atendimento 24 horas, inclusive fim de semana', 'Coleta nome, interesse e contato', 'Passa a conversa para sua equipe quando precisa']),
    ('04', 'Anúncios no Google e Instagram', 'Campanhas para quem já está procurando o que você vende, na sua região.',
     ['Campanha por bairro, cidade ou região', 'Criativos e textos inclusos', 'Acompanhamento semanal', 'Relatório mensal simples']),
    ('05', 'Edição de vídeos', 'Reels e vídeos curtos que apresentam seus produtos, serviços e sua equipe.',
     ['Roteiro curto para gravar no celular', 'Edição com legenda e trilha', 'Formato para Reels, Stories e site', '4 vídeos por mês no plano mensal']),
    ('06', 'Sistemas sob medida', 'Agendamento online, área do cliente e sistemas web feitos para o jeito que sua empresa trabalha.',
     ['Agenda com horários disponíveis em tempo real', 'Confirmação e lembrete automáticos', 'Painel simples para a equipe', 'Integração com WhatsApp']),
]

def servicos_detalhe():
    rows = []
    for n, t, d, items in SERVICOS:
        left = col([H(t, 'fc_num', 'secondary', 'h2'), P(d, 'fc_lead')], gap_=(12, 12, 10, 10))
        right = col([LIST(items)], gap_=(0, 0, 0, 0))
        W(left, 50, 50, 50, 100); W(right, 50, 50, 50, 100)
        r = line_row([left, right], name='Serviço ' + t, landscape_dir='row', mobile_dir='column', gap_=(64, 40, 28, 20))
        r['settings'].update(dims('padding', (48, 0, 48, 0), (40, 0, 40, 0), (32, 0, 32, 0), (28, 0, 28, 0)))
        rows.append(r)
    return section('Serviços em detalhe', [col(rows, 'Lista de serviços', gap_=(0, 0, 0, 0))], 'branco', 'servicos', py=(56, 48, 40, 32))

def inclusos():
    items = ['Layout pensado primeiro para o celular', 'Site rápido, que carrega em poucos segundos', 'Domínio e SSL configurados',
             'WhatsApp em todas as telas', 'Textos escritos para vender, revisados com você', 'Vídeo ensinando você a editar textos e fotos']
    head = col([H('O que já vem incluso em todos os planos')], name='Título da seção')
    a = col([LIST(items[:3])]); b = col([LIST(items[3:])])
    W(a, 50, 50, 100, 100); W(b, 50, 50, 100, 100)
    return section('Incluso em todos os planos', [head, row([a, b], name='Lista', gap_=(48, 32, 12, 12), tablet_dir='row')], 'branco')

def faq_list(qa, eye=None, title='Perguntas frequentes', bg='neutro50'):
    rows = []
    for q, a in qa:
        hq = H(q, 'fc_h3', 'secondary', 'h3'); pa = P(a)
        r = line_row([hq, pa], name=q[:40], landscape_dir='row', mobile_dir='column', gap_=(48, 32, 24, 6))
        W(hq, 45, 45, 45, 100); W(pa, 55, 55, 55, 100)
        rows.append(r)
    head = col([H(title)], name='Título da seção')
    return section(title, [head, col(rows, 'Lista', gap_=(0, 0, 0, 0))], bg, 'duvidas', gap_=(32, 32, 28, 24))

FAQ_PLANOS = [('Posso parcelar?', 'Sim. Os planos de pagamento único podem ser divididos em até 10x.'),
              ('Tem fidelidade no plano mensal?', 'Não. Você pode cancelar com 30 dias de aviso.'),
              ('Hospedagem e domínio estão inclusos?', 'O valor da hospedagem e do domínio é pago direto ao provedor, no seu nome. A gente contrata junto com você e configura tudo.'),
              ('Posso trocar de plano depois?', 'Sim. Quem começa com a landing page pode migrar para o site completo e o valor pago é abatido.')]

FAQ_SERV = [('Preciso ter fotos profissionais?', 'Ajuda muito, mas não é obrigatório. Orientamos você a fotografar a empresa e os produtos com o celular e tratamos as imagens.'),
            ('Vocês escrevem os textos?', 'Sim. Escrevemos pensando no seu cliente, e você revisa e aprova antes de publicar.'),
            ('Atendem fora da minha cidade?', 'Sim. Todo o processo é online, por vídeo e WhatsApp.')]

def caso(title, desc, link=None):
    kids = [H(title, 'fc_h3', 'secondary', 'h3'), P(desc)]
    if link: kids.append(B('Ver projeto', 'secondary', link, full_mobile=False))
    c = col(kids, gap_=(10, 10, 8, 8))
    return c

def portfolio_grid():
    feat = portfolio()['elements'][1]  # destaque GWmix com print real
    a = caso('Sistema de agendamento online', 'Agenda com horários disponíveis, confirmação automática e organização dos atendimentos.')
    b = caso('Landing pages para campanhas', 'Páginas de uma oferta só, feitas para receber tráfego de anúncios e levar ao WhatsApp.')
    r = line_row([a, b], name='Outros projetos', landscape_dir='row', mobile_dir='column', gap_=(48, 32, 24, 24))
    r['settings'].update(dims('padding', (40, 0, 0, 0), (32, 0, 0, 0), (28, 0, 0, 0), (24, 0, 0, 0)))
    W(a, 50, 50, 50, 100); W(b, 50, 50, 50, 100)
    return section('Projetos', [feat, r], 'branco', 'projetos', py=(72, 64, 48, 40), gap_=(56, 48, 40, 32))

def contato_bloco():
    def info(icon, lib, title, text):
        c = line_row([ICON(icon, lib, view='default', __globals__={'primary_color': C('primary')}, **slider('size', 20, l=20, m=20)), col([H(title, 'fc_caption', 'text', 'p'), P(text, 'fc_lead', 'secondary')], gap_=(4, 4, 4, 4))],
                     gap_=(16, 16, 14, 14), tablet_dir='row', landscape_dir='row', mobile_dir='row', flex_align_items='center', flex_wrap='nowrap', flex_wrap_mobile='nowrap')
        W(c['elements'][1], 'fit'); c['elements'][1]['settings']['_flex_size'] = 'grow'
        c['elements'][0]['settings']['_flex_size'] = 'none'  # ícone não encolhe
        return c
    infos = col([info('fab fa-whatsapp', 'fa-brands', 'WhatsApp', '<a href="https://wa.me/5511916751926" style="color:inherit">(11) 91675-1926</a>'),
                 info('fas fa-envelope', 'fa-solid', 'E-mail', 'contato@fcstudio.com.br'),
                 info('fab fa-instagram', 'fa-brands', 'Instagram', '@fcstudio'),
                 info('fas fa-clock', 'fa-solid', 'Atendimento', 'Segunda a sexta, das 9h às 18h')], name='Canais', gap_=(0, 0, 0, 0))
    fld = lambda _id, label, t='text', req=True, width='100': {'_id': _id, 'custom_id': _id, 'field_type': t, 'field_label': label, 'placeholder': label,
                                                            'required': 'true' if req else '', 'width': width}
    form = w('form', form_name='Contato FC Studio', form_fields=[fld('nome', 'Seu nome'), fld('empresa', 'Nome da empresa', req=False),
                                                                 fld('whatsapp', 'WhatsApp com DDD', 'tel'), fld('email', 'E-mail', 'email', False),
                                                                 fld('mensagem', 'O que você precisa?', 'textarea', False),
                                                                 {**fld('lgpd', 'Aceite', 'acceptance'), 'acceptance_text': 'Concordo em ser contatado pela FC Studio e com a Política de Privacidade.'}],
             button_text='Enviar mensagem', button_size='md', button_width='100', show_labels='',
             email_to='contato@fcstudio.com.br', email_subject='Novo contato pelo site FC Studio', success_message='Recebemos sua mensagem. Respondemos em até 1 dia útil.',
             submit_actions=['email', 'save-to-database'],
             __globals__={'field_typography_typography': T('fc_body'), 'field_text_color': C('secondary'), 'button_typography_typography': T('fc_button'),
                          'button_background_color': C('primary'), 'button_text_color': C('preto'), 'field_border_color': C('linha'), 'field_background_color': C('preto')},
             **slider('column_gap', 12, l=12, m=12), **slider('row_gap', 12, l=12, m=12),
             **radius('field_border_radius', 12, 12, 12), **radius('button_border_radius', 6, 6, 6))
    fcard = card([H('Mande uma mensagem', 'fc_h3', 'secondary', 'h2'), P('Respondemos em até 1 dia útil.'), form], pad=(32, 28, 24, 20), gap_=(12, 12, 12, 12), r=20,
                 _title='Formulário', css_classes='fc-borda')
    W(infos, 40, 100, 45, 100); W(fcard, 60, 100, 55, 100)
    r_ = row([infos, fcard], name='Contato', gap_=(48, 32, 24, 24), tablet_dir='column', landscape_dir='row', flex_align_items='flex-start')
    return section('Canais e formulário', [r_], 'branco', 'contato-form', py=(88, 72, 56, 56))

def quem_somos(tag='h2'):
    # slide "Sobre mim": foto com brilho verde à esquerda, texto à direita. Foto da Fab entra no lugar do logo quando chegar.
    img = IMG('equipe', 'Fabi e Clau, fundadoras da FC Studio')
    img['settings']['_css_classes'] = 'fc-foto'  # PNG recortado, sem contorno
    for k in [k for k in img['settings'] if k.startswith('image_border_radius')]: del img['settings'][k]
    foto = con([img], content_width='full', flex_direction='column', flex_justify_content='flex-end', flex_align_items='center', css_classes='fc-glow', _title='Foto com brilho',
               **dims('padding', (120, 0, 0, 0), (96, 0, 0, 0), (72, 0, 0, 0), (64, 0, 0, 0)))
    traco = w('html', html='<div class="fc-traco" aria-hidden="true"></div>', _title='Traço com ponto')
    texto = col([traco, H('Muito prazer, somos a FC Studio', 'fc_caption', 'primary', 'p'),
                 H('Não criamos apenas telas, construímos <span class="fc-verde">soluções de negócio.</span>', 'fc_h2', 'secondary', tag, _css_classes='fc-barra'),
                 P('Fundada por <strong>Fabi e Clau</strong>, a FC Studio nasceu para ir além das interfaces bonitas. Unimos a nossa expertise em <strong>estratégia</strong> e <strong>UI/UX Design</strong> para transformar a jornada do seu usuário em <strong>resultados reais de vendas</strong>.', 'fc_lead', 'cinza300'),
                 P('Desenhamos fluxos inteligentes e intuitivos que guiam seu cliente até o <strong>momento da compra</strong> sem fricção, acompanhando os dados de perto para garantir a melhor performance.', 'fc_body', 'text'),
                 B('Solicite um orçamento', 'primary', U('orcamento'))], name='Texto', gap_=(24, 22, 20, 18))
    W(texto, 54, 100, 100, 100)
    r_ = row([foto, texto], name='Quem somos · conteúdo', gap_=(72, 48, 40, 32), tablet_dir='column', flex_align_items='center')
    W(foto, 46, 80, 80, 100)
    return section('Quem somos', [r_], 'preto', 'quem-somos', css_classes='fc-estrelas')

def home_page():
    return mark_inner([hero(), beneficios(), servicos(), como_funciona(), planos(), portfolio(), faq(), cta()])

def servicos_page():
    return mark_inner([page_hero('Serviços', 'Tudo o que seu negócio precisa para vender mais online',
                                 'Do site ao chatbot, cada serviço foi pensado para transformar visita em cliente.',
                                 [B('Conversar no WhatsApp', 'primary'), B('Ver planos', 'secondary', U('planos'))]),
                       servicos_detalhe(), como_funciona(), faq_list(FAQ_SERV), cta()])

def planos_page():
    p_ = planos(); p_['elements'] = p_['elements'][1:]  # sem o título repetido
    p_['settings'].update(dims('padding', (40, 0, 88, 0), (32, 40, 72, 40), (24, 40, 56, 40), (24, 24, 56, 24), te=(40, 32, 88, 32)))
    return mark_inner([page_hero('Planos', 'Escolha o plano do seu negócio', 'Pagamento em até 10x. Sem fidelidade nos planos mensais.'),
                       p_, inclusos(), faq_list(FAQ_PLANOS), cta()])

def portfolio_page():
    return mark_inner([page_hero('Portfólio', 'Projetos entregues', 'Sites, landing pages e sistemas feitos para empresas de vários segmentos.'),
                       portfolio_grid(), cta()])

def contato_page():
    return mark_inner([page_hero('Contato', 'Vamos conversar sobre o seu negócio',
                                 'Chame no WhatsApp ou mande uma mensagem. Em 30 minutos de conversa você sai com um plano claro.',
                                 [B('Chamar no WhatsApp', 'primary')]),
                       contato_bloco()])

def principios():
    items = [('Estratégia antes da tela', 'Começamos pelo seu cliente e pelo seu objetivo de venda, não por um modelo pronto.'),
             ('Fluxos que levam à compra', 'Cada página tem um caminho claro até o WhatsApp, o formulário ou o carrinho.'),
             ('Acompanhamento depois do lançamento', 'Medimos o que funciona e ajustamos com você nos meses seguintes.')]
    rows = []
    for t, d in items:
        a = H(t, 'fc_h3', 'secondary', 'h3'); b = P(d)
        r = line_row([a, b], name=t, landscape_dir='row', mobile_dir='column', gap_=(32, 24, 20, 6))
        W(a, 40, 40, 40, 100); W(b, 60, 60, 60, 100)
        rows.append(r)
    head = col([H('Como trabalhamos'), P('Strategic UI/UX Design na prática: design que existe para gerar contato e venda.', 'fc_lead')], name='Título da seção', gap_=(20, 18, 16, 14))
    lst = col(rows, 'Princípios', gap_=(0, 0, 0, 0))
    W(head, 42, 100, 100, 100); W(lst, 58, 100, 100, 100)
    return section('Como trabalhamos', [row([head, lst], name='Princípios · conteúdo', gap_=(80, 40, 32, 28), tablet_dir='column')], 'neutro50', 'principios')

def quem_somos_page():
    return mark_inner([quem_somos('h1'), principios(), como_funciona(), cta()])

# ---------- orçamento: briefings como formulário em etapas ----------
def F(_id, label, t='text', req=False, width='100', options=None, inline=False):
    f = {'_id': _id, 'custom_id': _id, 'field_type': t, 'field_label': label, 'placeholder': '', 'required': 'true' if req else '', 'width': width}
    if options: f['field_options'] = '\n'.join(options)
    if inline: f['inline_list'] = 'elementor-subgroup-inline'
    return f

def STEP(_id, label, first=False, last=False):
    return {'_id': _id, 'custom_id': _id, 'field_type': 'step', 'field_label': label, 'previous_button': '' if first else 'Voltar', 'next_button': 'Próximo', 'width': '100'}

SIM_NAO = ['Sim', 'Não', 'Não sei']
CONTATO = lambda: [STEP('s1', 'Seus dados', first=True), F('nome', 'Nome e sobrenome', req=True, width='50'), F('email', 'E-mail', 'email', True, '50'),
                   F('whatsapp', 'WhatsApp com DDD', 'tel', True, '50'), F('negocio', 'Nome do negócio', req=True, width='50')]
VISUAL = lambda extra=(): [F('cores', 'Cores que você quer usar (ou deixe em branco para nos dar liberdade)'), F('cores_nao', 'Cores que não quer de jeito nenhum'), *extra,
                           F('obs', 'Mais alguma coisa que precisamos saber?', 'textarea'),
                           {**F('lgpd', 'Aceite', 'acceptance', True), 'acceptance_text': 'Concordo em ser contatado pela FC Studio e com a Política de Privacidade.'}]

BRIEFINGS = [
    ('site', 'Site institucional', 'Para empresas que querem ser encontradas no Google e passar confiança.', CONTATO() + [
        STEP('s2', 'Seu negócio'),
        F('sobre', 'Fale da sua empresa: o que faz, quem é o seu público e qual a missão', 'textarea', True),
        F('concorrentes', 'Principais concorrentes (com o link do site, se tiver)', 'textarea'),
        STEP('s3', 'O site'),
        F('objetivo', 'Objetivos do site: produtos, serviços e ideias que quer mostrar', 'textarea', True),
        F('acao', 'O que o visitante deve fazer no site?', 'select', True, options=['Pedir orçamento', 'Chamar no WhatsApp', 'Comprar', 'Fazer uma inscrição', 'Conhecer a empresa', 'Outro']),
        F('dominio', 'Já tem domínio? (ex.: www.suaempresa.com.br)', 'radio', True, '50', SIM_NAO, True),
        F('hospedagem', 'Já tem hospedagem para WordPress?', 'radio', True, '50', SIM_NAO, True),
        F('site_atual', 'Site atual, se tiver', 'url'),
        F('referencias', '3 sites que você gosta, para usarmos de referência', 'textarea'),
        STEP('s4', 'Visual'),
        F('estilo', 'Como o site deve parecer? Marque quantas quiser', 'checkbox', options=['Moderno', 'Sério', 'Conservador', 'Descontraído', 'Popular', 'Singular', 'Pesado', 'Leve'], inline=True),
        F('transmitir', 'Mensagem que o site deve passar (ex.: confiança, criatividade)', width='50'), F('nao_transmitir', 'E o que ele NÃO deve passar?', width='50'),
    ] + VISUAL([F('botao_whats', 'Quer botão de WhatsApp fixo no site?', 'radio', options=['Sim', 'Não'], inline=True)])),
    ('landing', 'Landing page', 'Uma página, uma oferta: para vender um produto ou captar contatos com anúncios.', CONTATO() + [
        STEP('s2', 'O produto'),
        F('tipo', 'Tipo de negócio', 'radio', True, options=['E-commerce', 'Infoproduto', 'Encapsulado', 'Negócio físico', 'Outro'], inline=True),
        F('produto', 'Qual produto ou oferta a página vai vender?', req=True),
        F('descricao', 'Descreva o produto e o público que quer alcançar', 'textarea', True),
        F('preco', 'Preço de comparação e de venda (ex.: de R$ 297 por R$ 197)', width='50'), F('site_atual', 'Site ou página atual, se tiver', 'url', width='50'),
        STEP('s3', 'A venda'),
        F('video', 'Tem vídeo de vendas?', 'radio', options=['Sim, já está no YouTube ou Vimeo', 'Ainda não', 'Não vou usar vídeo'], inline=True),
        F('gateway', 'Plataforma de pagamento (ex.: Hotmart, Kiwify, Mercado Pago)', width='50'), F('parcelamento', 'Parcela sem juros? Em quantas vezes?', width='50'),
        F('frete', 'Frete grátis?', 'radio', options=['Sim', 'Não', 'Não se aplica'], inline=True),
        F('depoimentos', 'Tem depoimentos de clientes?', 'radio', options=['Sim, em vídeo', 'Sim, em print ou texto', 'Ainda não'], inline=True),
        F('faq', 'Perguntas frequentes para a página', 'radio', options=['Tenho e vou enviar', 'Quero ajuda para montar', 'Não quero'], inline=True),
        F('dominio', 'Domínio', 'radio', options=['Já tenho', 'Preciso de um', 'Não sei'], inline=True),
        STEP('s4', 'Visual'),
        F('referencias', 'Páginas que você gosta, para usarmos de referência', 'textarea'),
    ] + VISUAL()),
    ('loja', 'Loja virtual', 'E-commerce completo, com catálogo, carrinho e pagamento.', CONTATO() + [
        STEP('s2', 'A loja'),
        F('loja', 'Nome da loja', req=True, width='50'), F('logo', 'Já tem logo?', 'radio', width='50', options=['Sim', 'Não, preciso de um'], inline=True),
        F('nicho', 'Segmento da loja', req=True, width='50'), F('publico', 'Público-alvo (ex.: mães de 25 a 40 anos)', req=True, width='50'),
        F('categorias', 'Categorias de produtos', 'textarea'),
        F('qtd', 'Quantos produtos, mais ou menos?', 'select', True, options=['Até 20', '21 a 100', '101 a 500', 'Mais de 500']),
        STEP('s3', 'As vendas'),
        F('wordpress', 'Já tem WordPress ou hospedagem?', 'radio', options=SIM_NAO, inline=True),
        F('gateway', 'Plataforma de pagamento (ex.: Mercado Pago, PagSeguro)', width='50'), F('parcelamento', 'Parcela sem juros? Em quantas vezes?', width='50'),
        F('frete', 'Frete grátis?', 'radio', options=['Sim', 'Não', 'Depende da região'], inline=True),
        F('depoimentos', 'Depoimentos de clientes', 'radio', options=['Tenho e vou enviar', 'Ainda não tenho', 'Não quero'], inline=True),
        F('banners', 'O que destacar nos banners da página inicial (até 3 mensagens)', 'textarea'),
        STEP('s4', 'Visual'),
        F('redes', 'Instagram e Facebook da loja'),
    ] + VISUAL()),
    ('artes', 'Artes para anúncios', 'Criativos para Instagram, Facebook e banners de loja.', CONTATO() + [
        STEP('s2', 'O criativo'),
        F('formatos', 'Formatos', 'checkbox', True, options=['Feed (1080 x 1080)', 'Stories (1080 x 1920)', 'Capa do Facebook (820 x 312)', 'Banner de loja (1280 x 400 e 680 x 400)', 'Imagem de categoria (1080 x 1080)', 'Outro formato']),
        F('qtd', 'Quantas artes?', 'number', width='50'), F('publico', 'Público-alvo (ex.: mulheres de 30 a 50 anos)', req=True, width='50'),
        F('frases', 'Frases exatas que vão na arte (curtas e diretas)', 'textarea', True),
        F('elementos', 'Algum elemento obrigatório? (ex.: foto de uma pessoa, selo de Black Friday, frete grátis)', 'textarea'),
        STEP('s3', 'Visual'),
    ] + VISUAL()),
]

def briefing_form(slug, title, fields):
    return w('form', form_name='Orçamento: ' + title, form_fields=fields, button_text='Enviar briefing', button_size='md', button_width='100', show_labels='true', mark_required='yes',
             step_type='number_text', step_icon_shape='circle',
             step_inactive_primary_color='#8A8A8A', step_inactive_secondary_color='#1A1A1A', step_active_primary_color='#00E600', step_active_secondary_color='#050505',
             step_completed_primary_color='#00A818', step_completed_secondary_color='#0B2B12',
             email_to='contato@fcstudio.com.br', email_subject='Pedido de orçamento: ' + title, success_message='Recebemos seu briefing. Mandamos o orçamento pelo WhatsApp em até 1 dia útil.',
             submit_actions=['email', 'save-to-database'], _css_classes='fc-form',
             __globals__={'field_typography_typography': T('fc_body'), 'label_typography_typography': T('fc_body'), 'label_color': C('secondary'), 'field_text_color': C('secondary'),
                          'button_typography_typography': T('fc_button'), 'button_background_color': C('primary'), 'button_text_color': C('preto'),
                          'previous_button_background_color': C('linha'), 'previous_button_text_color': C('secondary'),
                          'field_border_color': C('linha'), 'field_background_color': C('preto')},
             **slider('column_gap', 16, l=12, m=12), **slider('row_gap', 20, l=16, m=16), **slider('label_spacing', 8, l=6, m=6),
             **radius('field_border_radius', 6, 6, 6), **radius('button_border_radius', 6, 6, 6))

def orcamento_page():
    nav = row([B(t, 'secondary', '#orc-' + sl, full_mobile=True) for sl, t, _, _ in BRIEFINGS], name='Escolha o serviço', gap_=(12, 12, 10, 10), tablet_dir='row', landscape_dir='row', mobile_dir='column', flex_wrap='wrap')
    for b in nav['elements']: W(b, 'fit')
    top = page_hero('Orçamento', 'Solicite um orçamento',
                    'Escolha o serviço e responda o briefing. Leva uns 5 minutos e já traz tudo o que precisamos para mandar o valor certo, sem ida e volta.', [nav])
    W(top['elements'][0], 100, 100, 100, 100)
    top['elements'][0]['elements'].append(P('Chatbot, edição de vídeo ou sistema sob medida? <a href="https://wa.me/5511916751926" style="color:#00E600;font-weight:700;text-decoration:none">Chame no WhatsApp</a> que a gente conversa.', 'fc_body', 'text'))
    secs = [top]
    for i, (sl, t, d, fields) in enumerate(BRIEFINGS):
        head = col([H(t), P(d, 'fc_lead'), P('Os campos com * são obrigatórios. Senhas e acessos nunca vão por aqui: pedimos depois, por um canal seguro.', 'fc_body', 'text')], name='Título', gap_=(20, 18, 16, 14))
        fcard = card([briefing_form(sl, t, fields)], pad=(40, 32, 24, 20), _title='Briefing ' + t, css_classes='fc-borda')
        W(head, 34, 100, 100, 100); W(fcard, 66, 100, 100, 100)
        secs.append(section('Briefing ' + t, [row([head, fcard], name=t, gap_=(56, 32, 28, 24), tablet_dir='column', flex_align_items='flex-start')],
                            'neutro50' if i % 2 == 0 else 'preto', 'orc-' + sl, py=(96, 72, 56, 48)))
    return mark_inner(secs)

def header_tpl():
    return mark_inner([header()])

def footer_tpl():
    f = footer()
    f['elements'].append(whatsapp_float())  # dentro de um container, senão o "fixo" do Elementor não pega
    return mark_inner([f])

PAGES = [('home', 'Home', home_page), ('servicos', 'Serviços', servicos_page), ('planos', 'Planos', planos_page),
         ('portfolio', 'Portfólio', portfolio_page), ('quem-somos', 'Quem Somos', quem_somos_page), ('orcamento', 'Orçamento', orcamento_page), ('contato', 'Contato', contato_page)]

# Montserrat local: o plugin copia as fontes para wp-content/uploads/fcstudio-fonts e troca fc-fonts:// pelo endereço
FONTFACE = ''.join("@font-face{font-family:'Montserrat';font-style:normal;font-weight:%d;font-display:swap;src:url(fc-fonts://montserrat-%s.woff2) format('woff2')}" % (w_, n)
                   for w_, n in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold')))
# Morganite (arquivo original, sem alteração, conforme a licença do autor)
FONTFACE += "@font-face{font-family:'Morganite';font-style:normal;font-weight:100 900;font-display:swap;src:url(fc-fonts://morganite-ExtraBold.ttf) format('truetype')}"

# Detalhes dos slides. --px vale 1px no desktop e vira vw no celular (base 740 na paisagem, 390 no retrato).
CSS = (
    ':root{--px:1px}@media(max-width:880px){:root{--px:calc(100vw/740)}}@media(max-width:575px){:root{--px:calc(100vw/390)}}'
    'body{background:#050505}'
    'h2,h3{text-wrap:balance}p{text-wrap:pretty}'
    # fundo de estrelas
    '.fc-estrelas.e-con{background-image:url(fc-fonts://estrelas.jpg);background-repeat:repeat;background-size:calc(1200*var(--px))}'
    # texto em gradiente verde (vale por linha)
    '.fc-verde{background:linear-gradient(180deg,#00F000 0%,#00B100 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;'
    '-webkit-box-decoration-break:clone;box-decoration-break:clone}'
    '.fc-display{display:block;font-family:Morganite,"Arial Narrow",sans-serif;font-weight:800;font-size:2.7em;line-height:.9;letter-spacing:.005em;margin-top:.06em}'
    # barrinha verde antes do título de seção
    '.fc-barra .elementor-heading-title{border-left:.055em solid #00D61A;padding-left:.2em}'
    # traço horizontal com ponto (slide Sobre mim)
    '.fc-traco{position:relative;height:calc(12*var(--px))}'
    '.fc-traco:before{content:"";position:absolute;left:0;top:0;width:calc(12*var(--px));height:calc(12*var(--px));border-radius:50%;background:#00E600;box-shadow:0 0 calc(12*var(--px)) #00E600}'
    '.fc-traco:after{content:"";position:absolute;left:calc(6*var(--px));right:0;top:calc(5.5*var(--px));height:max(1px,calc(1*var(--px)));background:linear-gradient(90deg,#00D61A,rgba(0,214,26,.15))}'
    # linha vertical com ponto (slide Você está pronto)
    '.fc-linha-v.e-con{position:relative}'
    '.fc-linha-v.e-con:before{content:"";position:absolute;left:0;top:0;bottom:calc(6*var(--px));width:max(1px,calc(1*var(--px)));background:linear-gradient(180deg,rgba(0,214,26,.1),#00D61A)}'
    '.fc-linha-v.e-con:after{content:"";position:absolute;left:calc(-5.5*var(--px));bottom:0;width:calc(12*var(--px));height:calc(12*var(--px));border-radius:50%;background:#00E600;box-shadow:0 0 calc(12*var(--px)) #00E600}'
    # brilho atrás da foto
    '.fc-glow.e-con{background:radial-gradient(closest-side at 50% 50%,rgba(170,255,170,.9) 0%,#00E600 30%,rgba(0,190,20,.4) 62%,rgba(0,0,0,0) 100%)}'
    # seção clara com círculos (slide Escopo)
    '.fc-circulos.e-con{background-image:repeating-radial-gradient(circle at 92% 18%,rgba(0,0,0,0) 0 calc(46*var(--px)),rgba(0,0,0,.07) calc(46*var(--px)) calc(47.5*var(--px)))}'
    # botão com gradiente neon
    '.fc-neon .elementor-button{background-image:linear-gradient(180deg,#00E600,#00B100)}'
    '.elementor-button{transition:transform .2s cubic-bezier(.16,1,.3,1),box-shadow .2s}'
    '.elementor-button:hover{transform:translateY(-1px)}.fc-neon .elementor-button:hover{box-shadow:0 calc(10*var(--px)) calc(30*var(--px)) rgba(0,214,26,.35)}'
    # imagem e cartão em destaque: contorno verde com brilho; cartão comum: borda fina
    '.fc-offset img,.fc-offset.e-con{box-shadow:0 0 0 max(1px,calc(1*var(--px))) rgba(0,214,26,.6),0 0 calc(56*var(--px)) rgba(0,214,26,.18)}'
    '.fc-offset--cinza img{box-shadow:0 0 0 max(1px,calc(1*var(--px))) #2A2A2A}'
    '.fc-borda.e-con{border:max(1px,calc(1*var(--px))) solid #2A2A2A}'
    # textos
    '.elementor-widget-text-editor strong{color:#fff;font-weight:700}.fc-claro .elementor-widget-text-editor strong{color:#0A0A0A}'
    '.elementor-field-group .elementor-field::placeholder{color:#8A8A8A}'
    '.fc-form{--e-form-steps-divider-color:#2A2A2A}.fc-form .e-form__indicators__indicator__label{font-size:calc(11*var(--px));letter-spacing:.06em;text-transform:uppercase;font-weight:700;white-space:nowrap}@media(max-width:575px){.fc-form .e-form__indicators__indicator__label{white-space:normal;letter-spacing:.02em;font-size:calc(10*var(--px))}}'
    '.fc-form .elementor-field-label{font-weight:600}.fc-form .elementor-field-option label{color:#CBD2D9}.fc-form select.elementor-field{color:#fff}'
    '.fc-form .elementor-field-type-acceptance label{color:#A3A3A3;font-weight:400}'
    '::selection{background:#00D61A;color:#050505}:focus-visible{outline:2px solid #00E600;outline-offset:3px;border-radius:4px}'
    'html{scrollbar-color:#00D61A #050505;accent-color:#00D61A}a{text-underline-offset:.2em}'
)

def kit_settings():
    s = {
        'system_colors': [{'_id': i, 'title': t, 'color': c} for i, t, c in COLORS_SYS],
        'custom_colors': [{'_id': i, 'title': t, 'color': c} for i, t, c in COLORS_CUSTOM],
        'system_typography': [
            {'_id': 'primary', 'title': 'Títulos', 'typography_typography': 'custom', 'typography_font_family': DISPLAY, 'typography_font_weight': '800'},
            {'_id': 'secondary', 'title': 'Subtítulos', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '700'},
            {'_id': 'text', 'title': 'Texto', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '400'},
            {'_id': 'accent', 'title': 'Destaque', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '600'}],
        'custom_typography': [typo_preset(*t) for t in TYPO],
        'default_generic_fonts': 'Sans-serif',
        'body_background_background': 'classic', 'body_background_color': '#050505',
        'body_typography_typography': 'custom', 'body_typography_font_family': TEXT,
        'body_color': '#A3A3A3',
        # largura util: conteudo 1140 px no desktop, 1320 px em telas grandes; abaixo disso ocupa 100% e o respiro vem do padding das secoes
        'container_width': {'unit': 'px', 'size': 1140},
        'container_width_widescreen': {'unit': 'px', 'size': 1320},
        'container_width_laptop': {'unit': 'px', 'size': 1140},
        'container_width_tablet_extra': {'unit': '%', 'size': 100},
        'container_width_tablet': {'unit': '%', 'size': 100},
        'container_width_mobile_extra': {'unit': '%', 'size': 100},
        'container_width_mobile': {'unit': '%', 'size': 100},
        'container_padding': {'unit': 'px', 'top': '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': True},
        'space_between_widgets': {'unit': 'px', 'size': 0, 'column': '0', 'row': '0', 'isLinked': True},
        'page_title_selector': 'h1.entry-title',
        # 7 breakpoints: desktop (base) + 6 adicionais
        'active_breakpoints': ['viewport_mobile', 'viewport_mobile_extra', 'viewport_tablet', 'viewport_tablet_extra', 'viewport_laptop', 'viewport_widescreen'],
        'viewport_mobile': 575, 'viewport_mobile_extra': 880, 'viewport_tablet': 1024, 'viewport_tablet_extra': 1200, 'viewport_laptop': 1366, 'viewport_widescreen': 2400,
        'site_name': 'FC Studio', 'site_description': 'Strategic UI/UX Design',
        # detalhes do navegador com a cor da marca (seleção, foco, barra de rolagem, sublinhado)
        'custom_css': FONTFACE + CSS,
    }
    return s

if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'paginas'), exist_ok=True)
    json.dump(kit_settings(), open(os.path.join(OUT, 'kit-settings.json'), 'w'), ensure_ascii=False, indent=1)
    out = lambda name, title, typ, content, ps: json.dump({'version': '0.4', 'title': title, 'type': typ, 'content': content, 'page_settings': ps},
                                                      open(os.path.join(OUT, 'paginas', name + '.json'), 'w'), ensure_ascii=False, indent=1)
    for slug, title, fn in PAGES:
        out(slug, 'FCStudio ' + title, 'page', fn(), {'template': 'elementor_header_footer', 'hide_title': 'yes'})
    out('cabecalho', 'FCStudio Cabeçalho', 'header', header_tpl(), {})
    out('rodape', 'FCStudio Rodapé', 'footer', footer_tpl(), {})
    print('ok')
