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
COLORS_SYS = [('primary', 'Verde 500', '#168A5B'), ('secondary', 'Grafite 900', '#1F2933'), ('text', 'Cinza 500 (texto)', '#6B7280'), ('accent', 'Areia 300', '#F2C98A')]
COLORS_CUSTOM = [('verde700', 'Verde 700', '#0F6643'), ('verde100', 'Verde 100', '#E3F2EB'), ('neutro50', 'Neutro 50', '#F6F8F7'), ('cinza300', 'Cinza 300', '#CBD2D9'), ('branco', 'Branco', '#FFFFFF')]
C = lambda cid: 'globals/colors?id=' + cid

DISPLAY = 'Anton'  # troque para Morganite depois de enviar a fonte em Elementor > Fontes personalizadas
TEXT = 'Montserrat'
# id, titulo, familia, peso, (D, T, L, M) px, line-height em, letter-spacing em, transform
TYPO = [
    ('fc_h1', 'Título hero (H1)', DISPLAY, '400', (88, 68, 52, 44), 0.98, 0, 'uppercase'),
    ('fc_h2', 'Título de seção (H2)', DISPLAY, '400', (56, 44, 38, 34), 1.05, 0.01, 'uppercase'),
    ('fc_num', 'Número / preço', DISPLAY, '400', (40, 36, 32, 30), 1.0, 0, 'uppercase'),
    ('fc_h3', 'Título de card (H3)', TEXT, '700', (24, 22, 20, 20), 1.3, 0, 'none'),
    ('fc_lead', 'Texto de apoio', TEXT, '500', (20, 18, 17, 17), 1.5, 0, 'none'),
    ('fc_body', 'Texto corpo', TEXT, '400', (16, 16, 15, 15), 1.6, 0, 'none'),
    ('fc_caption', 'Legenda / sobretítulo', TEXT, '600', (13, 13, 12, 12), 1.4, 0.12, 'uppercase'),
    ('fc_button', 'Botão', TEXT, '600', (16, 16, 15, 15), 1.0, 0.01, 'none'),
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
    if align: s['align'] = align
    s.update(extra)
    return w('heading', **s)

def P(text, tid='fc_body', color='text', **extra):
    s = {'editor': '<p>' + text + '</p>', '__globals__': {'typography_typography': T(tid), 'text_color': C(color)}}
    s.update(slider('paragraph_spacing', 0, l=0, m=0))  # o espaçamento vem do gap do container
    s.update(extra)
    return w('text-editor', **s)

WA = 'https://wa.me/5511916751926?text=Ol%C3%A1%2C%20quero%20saber%20mais%20sobre%20o%20site%20para%20meu%20consult%C3%B3rio'

def B(text, kind='primary', url=WA, full_mobile=True, **extra):
    bg, fg, border = {'primary': ('primary', 'branco', None), 'secondary': (None, 'primary', 'primary'),
                      'white': ('branco', 'verde700', None), 'dark': ('primary', 'branco', None)}[kind]
    s = {'text': text, 'link': {'url': url, 'is_external': url.startswith('http'), 'nofollow': ''},
         '__globals__': {'typography_typography': T('fc_button'), 'button_text_color': C(fg)}}
    s['background_color'] = '#00000000'
    if bg: s['__globals__']['background_color'] = C(bg)
    if border:
        s.update({'border_border': 'solid', '__globals__': {**s['__globals__'], 'border_color': C(border)}})
        s.update(slider('border_width', 2, l=2, m=2) and {'border_width': {'unit': 'px', 'top': '2', 'right': '2', 'bottom': '2', 'left': '2', 'isLinked': True},
                 'border_width_mobile_extra': {'unit': 'vw', 'top': str(vw(2, BASE_L)), 'right': str(vw(2, BASE_L)), 'bottom': str(vw(2, BASE_L)), 'left': str(vw(2, BASE_L)), 'isLinked': True},
                 'border_width_mobile': {'unit': 'vw', 'top': str(vw(2, BASE_M)), 'right': str(vw(2, BASE_M)), 'bottom': str(vw(2, BASE_M)), 'left': str(vw(2, BASE_M)), 'isLinked': True}})
    s.update(radius('border_radius', 10, 10, 10))
    s.update(dims('text_padding', (18, 28, 18, 28), (16, 26, 16, 26), (15, 24, 15, 24), (16, 22, 16, 22)))
    if full_mobile:
        s['align_mobile'] = 'justify'
    s.update(extra)
    return w('button', **s)

def ICON(icon, lib='fa-solid', **extra):
    s = {'selected_icon': {'value': icon, 'library': lib}, 'view': 'stacked', 'shape': 'square', 'align': 'left',
         '__globals__': {'primary_color': C('verde100'), 'secondary_color': C('verde700')}}
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

def section(name, children, bg='neutro50', css_id=None, py=(112, 88, 64, 64), px=(0, 40, 40, 24), gap_=(48, 40, 32, 32), te_px=32, **extra):
    s = {'_title': name, 'content_width': 'boxed', 'flex_direction': 'column', 'background_background': 'classic', '__globals__': {'background_color': C(bg)}}
    s.update(dims('padding', (py[0], px[0], py[0], px[0]), (py[1], px[1], py[1], px[1]), (py[2], px[2], py[2], px[2]), (py[3], px[3], py[3], px[3]), te=(py[0], te_px, py[0], te_px)))
    s.update(gap('flex_gap', *gap_))
    if css_id: s['_element_id'] = css_id
    s.update(extra)
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

def card(children, bg='branco', pad=(32, 28, 24, 24), gap_=(12, 12, 10, 10), r=16, **extra):
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
                          '__globals__': {**r['settings'].get('__globals__', {}), 'border_color': C('cinza300')}})
    r['settings'].update(dims('padding', (28, 0, 28, 0), (24, 0, 24, 0), (20, 0, 20, 0), (20, 0, 20, 0)))
    r['settings']['border_width_mobile_extra'] = {'unit': 'vw', 'top': str(vw(1, BASE_L)) if top else '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False}
    r['settings']['border_width_mobile'] = {'unit': 'vw', 'top': str(vw(1, BASE_M)) if top else '0', 'right': '0', 'bottom': '0', 'left': '0', 'isLinked': False}
    return r

def IMG(token, alt, r=14):
    s = {'image': {'url': 'fc-img://' + token, 'id': 'fc-imgid://' + token, 'alt': alt}, 'image_size': 'full', '_title': 'Imagem ' + token}
    s.update(slider('width', 100, l=100, m=100)); s['width'] = {'unit': '%', 'size': 100}
    for k in ('width_tablet', 'width_mobile_extra', 'width_mobile'): s[k] = {'unit': '%', 'size': 100}
    s.update(radius('image_border_radius', r, r - 2, r - 4))
    s['image_box_shadow_box_shadow_type'] = 'yes'
    s['image_box_shadow_box_shadow'] = {'horizontal': 0, 'vertical': 24, 'blur': 48, 'spread': -12, 'color': 'rgba(31,41,51,0.28)'}
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
    s = {'html': logo_svg('#FFFFFF' if light else '#168A5B', '#FFFFFF' if light else '#1F2933'), '_element_width': 'initial'}
    s.update(slider('_element_custom_width', width_d, l=l, m=m))
    s['_title'] = 'Logo FCStudio'
    return w('html', **s)

# ---------- página ----------
def header():
    # Menu do Pro Elements: horizontal no desktop/laptop/tablet paisagem, hambúrguer a partir do tablet retrato
    nav = w('nav-menu', menu='menu-principal', layout='horizontal', pointer='none', dropdown='tablet', toggle='burger', full_width='stretch', toggle_align='right', align_items='right',
            text_align='aside', _title='Menu',
            __globals__={'menu_typography_typography': T('fc_button'), 'color_menu_item': C('secondary'), 'color_menu_item_hover': C('primary'),
                         'dropdown_typography_typography': T('fc_button'), 'color_dropdown_item': C('secondary'), 'background_color_dropdown_item': C('branco'),
                         'color_dropdown_item_hover': C('branco'), 'background_color_dropdown_item_hover': C('primary'), 'toggle_color': C('secondary'), 'toggle_background_color': C('verde100')},
            **slider('padding_horizontal_menu_item', 16, 14, 14, 14), **slider('toggle_size', 22, 22, 24, 24), **slider('toggle_border_width', 0, 0, 0, 0),
            **radius('toggle_border_radius', 10, 10, 10), **slider('dropdown_top_distance', 12, 12, 12, 12),
            **slider('padding_horizontal_dropdown_item', 40, 40, 40, 24), **slider('padding_vertical_dropdown_item', 14, 14, 14, 14))
    cta = B('Falar no WhatsApp', 'primary', full_mobile=False, hide_mobile='hidden-mobile', hide_mobile_extra='hidden-mobile_extra')
    s = {'_title': 'Cabeçalho', 'content_width': 'boxed', 'flex_direction': 'row', 'flex_direction_mobile': 'row', 'flex_direction_mobile_extra': 'row', 'flex_direction_tablet': 'row',
         'flex_justify_content': 'space-between', 'flex_align_items': 'center', 'flex_wrap': 'nowrap',
         'background_background': 'classic', '__globals__': {'background_color': C('branco')}, 'z_index': 100 }
    s.update(dims('padding', (16, 0, 16, 0), (14, 40, 14, 40), (12, 40, 12, 40), (12, 24, 12, 24), te=(16, 32, 16, 32)))
    s.update(gap('flex_gap', 24, 16, 16, 12))
    right = row([nav, cta], name='Direita', gap_=(32, 16, 12, 12), mobile_dir='row', landscape_dir='row', flex_align_items='center', flex_justify_content='flex-end')
    W(right, 'fit')
    lg = LOGO(64, l=60, m=52); lg['settings']['html'] = '<a href="fc://home" aria-label="FCStudio, página inicial" style="display:block">' + lg['settings']['html'] + '</a>'
    return con([lg, right], **s)

def hero():
    buttons = row([B('Quero mais pacientes', 'primary'), B('Ver planos', 'secondary', U('planos'))], name='Botões', gap_=(12, 12, 12, 10), landscape_dir='row', mobile_dir='column')
    text = col([H('Sites que enchem a agenda do seu consultório', 'fc_h1', 'secondary', 'h1'),
                P('Seu paciente encontra você no Google, confia no que vê e agenda pelo WhatsApp. A FCStudio cuida do site, dos anúncios e dos vídeos.', 'fc_lead'),
                buttons, P('Site no ar em 15 dias &nbsp;·&nbsp; Suporte por 3 meses &nbsp;·&nbsp; Textos dentro das regras do CFO', 'fc_body')],
               name='Texto', gap_=(28, 24, 20, 18))
    proof = col([IMG('gwmix', 'Site da GWmix feito pela FCStudio'),
                 P('Último projeto entregue: <a href="https://gwmix.ind.br" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;text-underline-offset:.2em">gwmix.ind.br</a>', 'fc_body')],
                name='Prova: projeto real', gap_=(14, 12, 12, 10))
    W(text, 50, 100); W(proof, 50, 100)
    r_ = row([text, proof], name='Hero · conteúdo', gap_=(64, 48, 36, 40), tablet_dir='column', flex_align_items='center')
    return section('Hero', [r_], 'neutro50', 'inicio', py=(88, 64, 48, 40))

def beneficios():
    items = [('Aparece no Google', 'Site rápido e preparado para buscas como "dentista perto de mim" na sua cidade.'),
             ('Passa confiança', 'Fotos reais, equipe, estrutura e tratamentos explicados sem jargão.'),
             ('Agenda pelo WhatsApp', 'Botão em todas as telas. O paciente chama você em um clique.')]
    rows = []
    for i, (t, d) in enumerate(items):
        a = H(t, 'fc_h3', 'secondary', 'h3'); b = P(d)
        r = line_row([a, b], name=t, landscape_dir='row', mobile_dir='column', gap_=(32, 24, 20, 6))
        W(a, 40, 40, 40, 100); W(b, 60, 60, 60, 100)
        rows.append(r)
    head = col([H('O paciente pesquisa antes de marcar'),
                P('A maioria dos pacientes procura o dentista no Google antes de agendar. Quem não aparece, não entra na lista.', 'fc_lead')], name='Título da seção', gap_=(20, 18, 16, 14))
    lst = col(rows, 'Lista', gap_=(0, 0, 0, 0))
    W(head, 42, 100, 100, 100); W(lst, 58, 100, 100, 100)
    return section('Benefícios', [row([head, lst], name='Benefícios · conteúdo', gap_=(80, 40, 32, 28), tablet_dir='column')], 'branco')

def servicos():
    items = [('Site para consultório', 'Site completo com tratamentos, equipe, localização e agendamento.'),
             ('Landing page por tratamento', 'Uma página focada em implante, lente de contato dental ou ortodontia.'),
             ('Anúncios no Google e Instagram', 'Campanhas para quem está procurando dentista agora, na sua região.'),
             ('Edição de vídeos', 'Reels e vídeos curtos que explicam tratamentos e mostram a clínica.'),
             ('Sistema de agendamento', 'Agenda online para o paciente marcar sozinho, integrada ao WhatsApp.')]
    rows = []
    for t, d in items:
        a = H(t, 'fc_h2', 'secondary', 'h3'); b = P(d, 'fc_lead')
        a['settings']['__globals__']['typography_typography'] = T('fc_num')
        r = line_row([a, b], name=t, landscape_dir='row', mobile_dir='column', gap_=(48, 32, 24, 8), flex_align_items='center')
        W(a, 50, 50, 50, 100); W(b, 50, 50, 50, 100)
        rows.append(r)
    head = row([H('Tudo o que seu consultório precisa para ser encontrado'), B('Ver os serviços', 'secondary', U('servicos'), full_mobile=False)],
               name='Título da seção', gap_=(32, 24, 20, 20), tablet_dir='row', landscape_dir='column', mobile_dir='column', flex_align_items='flex-end', flex_align_items_mobile='flex-start', flex_align_items_mobile_extra='flex-start', flex_justify_content='space-between')
    W(head['elements'][0], 70, 70, 100, 100); W(head['elements'][1], 'fit')
    return section('Serviços', [head, col(rows, 'Lista de serviços', gap_=(0, 0, 0, 0))], 'neutro50', 'servicos')

def como_funciona():
    steps = []
    for n, t, d in [('1', 'Conversa', '30 minutos por vídeo para entender seu consultório e seus pacientes.'),
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
    return section('Como funciona', [head, grid(steps, (4, 2, 2, 1), 'Passos', gap_=(32, 32, 24, 32))], 'branco', 'como-funciona')

def planos():
    data = [('Essencial', 'Landing page', 'R$ 1.490', 'pagamento único', ['1 página focada em um tratamento', 'Botão de WhatsApp em todas as telas', 'Domínio e SSL configurados', 'Entrega em 10 dias'], False),
            ('Consultório', 'Site completo', 'R$ 2.990', 'pagamento único', ['Até 6 páginas', 'Google Meu Negócio otimizado', 'Página de cada tratamento', '3 meses de suporte'], True),
            ('Agenda cheia', 'Site + marketing', 'R$ 1.290', 'por mês + implantação do site', ['Tudo do plano Consultório', 'Anúncios no Google e Instagram', '4 vídeos editados por mês', 'Relatório mensal de resultados'], False)]
    cards = []
    for nm, sub, price, per, items, hi in data:
        kids = []
        if hi:
            kids.append(H('Mais escolhido', 'fc_caption', 'secondary', 'p', _element_width='auto', _flex_align_self='flex-start', _background_background='classic',
                          **dims('_padding', (6, 12, 6, 12), (6, 12, 6, 12), (5, 10, 5, 10), (5, 10, 5, 10)), **radius('_border_radius', 999, 999, 999),
                          **{'__globals__': {'typography_typography': T('fc_caption'), 'title_color': C('secondary'), '_background_color': C('accent')}}))
        kids += [H(nm, 'fc_h3', 'branco' if hi else 'secondary', 'h3'), P(sub, 'fc_body', 'cinza300' if hi else 'text'),
                 H(price, 'fc_num', 'branco' if hi else 'primary', 'p'), H(per, 'fc_caption', 'cinza300' if hi else 'text', 'p'),
                 LIST(items, hi), B('Quero este plano', 'primary' if hi else 'secondary', full_mobile=True, align='justify')]
        c = card(kids, bg='secondary' if hi else 'branco', gap_=(16, 14, 14, 14), _title='Plano ' + nm)
        if hi:
            c['settings']['_flex_order_mobile'] = 'start'
        cards.append(c)
    head = col([eyebrow('Planos'), H('Escolha o plano do seu consultório'), P('Pagamento em até 10x. Sem fidelidade nos planos mensais.', 'fc_lead')], name='Título da seção')
    plans_row = row(cards, name='Cards de plano', gap_=(24, 16, 20, 16), tablet_dir='row', flex_align_items='stretch')
    for c in cards:
        W(c, 33.333, 33.333, 100, 100)
    # no celular o plano em destaque vem primeiro
    cards[1]['settings']['_flex_order_mobile'] = 'start'
    cards[1]['settings']['_flex_order_mobile_extra'] = 'start'
    return section('Planos', [head, plans_row], 'neutro50', 'planos')

def portfolio():
    img = IMG('gwmix', 'Site da GWmix feito pela FCStudio')
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
          ('O site segue as regras de publicidade do CFO?', 'Sim. Os textos não prometem resultado e seguem o Código de Ética Odontológica.')]
    return faq_list(qa)

def cta():
    return section('Chamada final', [eyebrow('Vamos conversar', True), H('Vamos encher sua agenda?', 'fc_h2', 'branco'),
                                     P('Conversa de 30 minutos, sem compromisso. Você sai com um plano claro para o seu consultório.', 'fc_lead', 'verde100'),
                                     B('Chamar no WhatsApp', 'white')], 'primary', 'contato', gap_=(20, 20, 18, 18))

def footer():
    c1 = col([LOGO(80, True, 70, 64), P('Sites e presença digital para dentistas e clínicas odontológicas.', 'fc_body', 'cinza300')], gap_=(16, 16, 14, 14), _flex_size='grow')
    def links(title, items):
        return col([H(title, 'fc_caption', 'verde100', 'p')] + [P(i, 'fc_body', 'branco') for i in items], gap_=(10, 10, 8, 8), _flex_size='grow')
    nav_ = links('Navegação', ['<a href="fc://servicos" style="color:inherit">Serviços</a>', '<a href="fc://planos" style="color:inherit">Planos</a>', '<a href="fc://portfolio" style="color:inherit">Portfólio</a>', '<a href="fc://contato" style="color:inherit">Contato</a>'])
    cont_ = links('Contato', ['<a href="https://wa.me/5511916751926" style="color:inherit">WhatsApp: (11) 91675-1926</a>', 'contato@fcstudio.com.br', 'Instagram: @fcstudio'])
    W(c1, 40, 40, 40, 100); W(nav_, 30, 30, 30, 100); W(cont_, 30, 30, 30, 100)
    cols_ = row([c1, nav_, cont_], name='Colunas', gap_=(64, 40, 32, 32), landscape_dir='row', mobile_dir='column')
    line = w('divider', **{'__globals__': {'color': C('text')}, **slider('weight', 1, l=1, m=1)})
    return section('Rodapé', [cols_, line, H('© 2026 FCStudio. Todos os direitos reservados.', 'fc_caption', 'cinza300', 'p')], 'secondary', 'rodape', py=(56, 48, 40, 40), gap_=(32, 28, 24, 24))

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
    return section(name, [text], 'neutro50', 'inicio', py=(96, 72, 48, 48))

SERVICOS = [
    ('01', 'Site para consultório', 'Site completo com tratamentos, equipe, localização e agendamento.',
     ['Até 6 páginas com textos dentro das regras do CFO', 'Página para cada tratamento', 'Mapa, horários e botão de WhatsApp', 'Google Meu Negócio otimizado']),
    ('02', 'Landing page por tratamento', 'Uma página focada em implante, lente de contato dental ou ortodontia.',
     ['Texto que explica o tratamento sem jargão', 'Perguntas frequentes do paciente', 'Formulário e WhatsApp no topo', 'Pronta para receber anúncios']),
    ('03', 'Anúncios no Google e Instagram', 'Campanhas para quem está procurando dentista agora, na sua região.',
     ['Campanha por bairro ou cidade', 'Criativos e textos inclusos', 'Acompanhamento semanal', 'Relatório mensal simples']),
    ('04', 'Edição de vídeos', 'Reels e vídeos curtos que explicam tratamentos e mostram a clínica.',
     ['Roteiro curto para gravar no celular', 'Edição com legenda e trilha', 'Formato para Reels, Stories e site', '4 vídeos por mês no plano mensal']),
    ('05', 'Sistema de agendamento', 'Agenda online para o paciente marcar sozinho, integrada ao WhatsApp.',
     ['Horários disponíveis em tempo real', 'Confirmação automática', 'Lembrete antes da consulta', 'Painel simples para a recepção']),
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
             'WhatsApp em todas as telas', 'Textos dentro das regras do CFO', 'Vídeo ensinando você a editar textos e fotos']
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

FAQ_SERV = [('Preciso ter fotos profissionais?', 'Ajuda muito, mas não é obrigatório. Orientamos você a fotografar a clínica com o celular e tratamos as imagens.'),
            ('Vocês escrevem os textos?', 'Sim. Você revisa e aprova. Todos seguem as regras de publicidade do CFO.'),
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
    form = w('form', form_name='Contato FCStudio', form_fields=[fld('nome', 'Seu nome'), fld('clinica', 'Nome do consultório ou clínica', req=False),
                                                                 fld('whatsapp', 'WhatsApp com DDD', 'tel'), fld('email', 'E-mail', 'email', False),
                                                                 fld('mensagem', 'O que você precisa?', 'textarea', False),
                                                                 {**fld('lgpd', 'Aceite', 'acceptance'), 'acceptance_text': 'Concordo em ser contatado pela FCStudio e com a Política de Privacidade.'}],
             button_text='Enviar mensagem', button_size='md', button_width='100', show_labels='',
             email_to='contato@fcstudio.com.br', email_subject='Novo contato pelo site FCStudio', success_message='Recebemos sua mensagem. Respondemos em até 1 dia útil.',
             submit_actions=['email', 'save-to-database'],
             __globals__={'field_typography_typography': T('fc_body'), 'field_text_color': C('secondary'), 'button_typography_typography': T('fc_button'),
                          'button_background_color': C('primary'), 'button_text_color': C('branco'), 'field_border_color': C('cinza300'), 'field_background_color': C('branco')},
             **slider('column_gap', 12, l=12, m=12), **slider('row_gap', 12, l=12, m=12),
             **radius('field_border_radius', 12, 12, 12), **radius('button_border_radius', 999, 999, 999))
    fcard = card([H('Mande uma mensagem', 'fc_h3', 'secondary', 'h2'), P('Respondemos em até 1 dia útil.'), form], pad=(32, 28, 24, 20), gap_=(12, 12, 12, 12), r=20,
                 _title='Formulário', box_shadow_box_shadow_type='yes',
                 box_shadow_box_shadow={'horizontal': 0, 'vertical': 16, 'blur': 40, 'spread': 0, 'color': 'rgba(31,41,51,0.10)'})
    W(infos, 40, 100, 45, 100); W(fcard, 60, 100, 55, 100)
    r_ = row([infos, fcard], name='Contato', gap_=(48, 32, 24, 24), tablet_dir='column', landscape_dir='row', flex_align_items='flex-start')
    return section('Canais e formulário', [r_], 'branco', 'contato-form', py=(88, 72, 56, 56))

def home_page():
    return mark_inner([hero(), beneficios(), servicos(), como_funciona(), planos(), portfolio(), faq(), cta()])

def servicos_page():
    return mark_inner([page_hero('Serviços', 'Tudo o que seu consultório precisa para ser encontrado',
                                 'Do site ao anúncio, cada serviço foi pensado para o paciente que pesquisa antes de marcar.',
                                 [B('Conversar no WhatsApp', 'primary'), B('Ver planos', 'secondary', U('planos'))]),
                       servicos_detalhe(), como_funciona(), faq_list(FAQ_SERV), cta()])

def planos_page():
    p_ = planos(); p_['elements'] = p_['elements'][1:]  # sem o título repetido
    p_['settings'].update(dims('padding', (40, 0, 88, 0), (32, 40, 72, 40), (24, 40, 56, 40), (24, 24, 56, 24), te=(40, 32, 88, 32)))
    return mark_inner([page_hero('Planos', 'Escolha o plano do seu consultório', 'Pagamento em até 10x. Sem fidelidade nos planos mensais.'),
                       p_, inclusos(), faq_list(FAQ_PLANOS), cta()])

def portfolio_page():
    return mark_inner([page_hero('Portfólio', 'Projetos entregues', 'Sites, landing pages e sistemas feitos para consultórios e clínicas.'),
                       portfolio_grid(), cta()])

def contato_page():
    return mark_inner([page_hero('Contato', 'Vamos conversar sobre o seu consultório',
                                 'Chame no WhatsApp ou mande uma mensagem. Em 30 minutos de conversa você sai com um plano claro.',
                                 [B('Chamar no WhatsApp', 'primary')]),
                       contato_bloco()])

def header_tpl():
    return mark_inner([header()])

def footer_tpl():
    f = footer()
    f['elements'].append(whatsapp_float())  # dentro de um container, senão o "fixo" do Elementor não pega
    return mark_inner([f])

PAGES = [('home', 'Home', home_page), ('servicos', 'Serviços', servicos_page), ('planos', 'Planos', planos_page),
         ('portfolio', 'Portfólio', portfolio_page), ('contato', 'Contato', contato_page)]

def kit_settings():
    s = {
        'system_colors': [{'_id': i, 'title': t, 'color': c} for i, t, c in COLORS_SYS],
        'custom_colors': [{'_id': i, 'title': t, 'color': c} for i, t, c in COLORS_CUSTOM],
        'system_typography': [
            {'_id': 'primary', 'title': 'Títulos', 'typography_typography': 'custom', 'typography_font_family': DISPLAY, 'typography_font_weight': '400'},
            {'_id': 'secondary', 'title': 'Subtítulos', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '700'},
            {'_id': 'text', 'title': 'Texto', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '400'},
            {'_id': 'accent', 'title': 'Destaque', 'typography_typography': 'custom', 'typography_font_family': TEXT, 'typography_font_weight': '600'}],
        'custom_typography': [typo_preset(*t) for t in TYPO],
        'default_generic_fonts': 'Sans-serif',
        'body_background_background': 'classic', 'body_background_color': '#F6F8F7',
        'body_typography_typography': 'custom', 'body_typography_font_family': TEXT,
        'body_color': '#6B7280',
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
        'site_name': 'FCStudio', 'site_description': 'Sites e presença digital para dentistas',
        # detalhes do navegador com a cor da marca (seleção, foco, barra de rolagem, sublinhado)
        'custom_css': '::selection{background:#168A5B;color:#fff}:focus-visible{outline:2px solid #168A5B;outline-offset:3px;border-radius:4px}html{scrollbar-color:#168A5B #F6F8F7;accent-color:#168A5B}a{text-underline-offset:.2em}.elementor-button{transition:transform .2s cubic-bezier(.16,1,.3,1),box-shadow .2s}.elementor-button:hover{transform:translateY(-1px)}',
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
