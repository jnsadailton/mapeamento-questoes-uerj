"""Leitura dos gabaritos comentados: um registro por comentário e um por classificação (eixo, item, subitem).

A ordem do texto nesses PDFs é embaralhada, então as linhas são ordenadas pela posição (página, y, x) e cada comentário
é ligado ao rótulo "QUESTÃO NN" que o antecede na página. O número do rótulo às vezes vem numa linha própria, antes ou
depois da palavra "QUESTÃO". O idioma do bloco de língua estrangeira e a área vêm do cabeçalho da página.
"""
import re

from .pdf_texto import linhas_pdf, sem_acento

IDIOMAS = {'ESPANHOL': 'ES', 'FRANCES': 'FR', 'INGLES': 'EN'}
ALTURA_CABECALHO = 45  # cabeçalho: faixa do topo, à direita da margem onde ficam os rótulos
MARGEM_ROTULO = 150

# Rótulos dos campos de um comentário, com as variações vistas nos PDFs ("Item:", "Subitens do programa:",
# "Item do programa do programa:"). O número opcional ("Item do programa 2:") indica a ordem da classificação.
CAMPOS = re.compile(
    r'(?P<campo>Eixo(?: (?:inter)?disciplinar)?|Subite(?:m|ns)(?:\s*do programa)*|Ite(?:m|ns)(?:\s*do programa)*'
    r'|Objetivo|Coment[áa]rio|Gabarito|Percentual de acertos?|N[íi]vel de dif+iculdade)(?:\s*(?P<ordem>\d))?\s*:',
    re.I)
CLASSIFICACAO = re.compile(r'Eixo|Subite(?:m|ns)\b|Ite(?:m|ns)\b', re.I)
NOMES = {'EIXO': 'eixo', 'SUBITE': 'subitem', 'ITE': 'item', 'OBJETIVO': 'objetivo', 'COMENTARIO': 'comentario',
         'GABARITO': 'gabarito', 'PERCENTUAL': 'percentual', 'NIVEL': 'nivel'}
# Valor dos campos que fecham o comentário. O que vier depois do último deles é texto da questão seguinte.
FINAIS = {
    'gabarito': re.compile(r'\s*(?:[A-D]\b|ANULADA)?\.?', re.I),
    'percentual': re.compile(r'\s*(?:\d+(?:[,.]\d+)?\s*%?)?\.?'),
    'nivel': re.compile(r'\s*(?:f[áa]cil|m[ée]dio|dif[íi]cil)?(?:\s*\([^)]*\))?\.?', re.I),
}


def _norm(t):
    return sem_acento(t).upper().strip()


def _rotulo(l):
    """Número do rótulo "QUESTÃO NN" (None se a linha não é rótulo; 0 se é rótulo sem número na mesma linha)."""
    m = re.fullmatch(r'QUESTAO\s*(\d{1,2})?', _norm(l['t']))
    return (int(m[1]) if m[1] else 0) if m else None


def _numero_perto(rotulo, linhas):
    """Número escrito numa linha própria ao lado do rótulo (acima, abaixo ou na mesma altura)."""
    # O número às vezes sai grudado num símbolo de fórmula vizinho ("28 {").
    perto = [l for l in linhas if l['p'] == rotulo['p'] and re.fullmatch(r'\d{1,2}(?: \S)?', l['t'])
             and abs(l['y'] - rotulo['y']) < 30 and abs(l['x'] - rotulo['x']) < 60]
    return int(min(perto, key=lambda l: abs(l['y'] - rotulo['y']))['t'].split()[0]) if perto else None


def _rodape(linhas):
    """Altura a partir da qual a linha é rodapé (onde fica 'Vestibular Estadual AAAA')."""
    ys = sorted(l['y'] for l in linhas if _norm(l['t']).startswith('VESTIBULAR ESTADUAL') and l['y'] > 500)
    return ys[len(ys) // 2] - 8 if ys else float('inf')


def _cabecalho(l):
    return l['y'] < ALTURA_CABECALHO and l['x'] > MARGEM_ROTULO


def _campos(texto):
    """Separa o texto do comentário pelos rótulos dos campos e corta o que sobra depois do último campo final.

    Devolve (texto cortado, lista de (campo, ordem, valor)).
    """
    ms = list(CAMPOS.finditer(texto))
    out = []
    for i, m in enumerate(ms):
        fim = ms[i + 1].start() if i + 1 < len(ms) else len(texto)
        campo = next(v for k, v in NOMES.items() if _norm(m['campo']).startswith(k))
        valor = texto[m.end():fim]
        if campo in FINAIS and i + 1 == len(ms):
            valor = FINAIS[campo].match(valor)[0]
            texto = texto[:m.end() + len(valor)]
        out.append((campo, int(m['ordem'] or 1), valor.strip()))
    return texto, out


def _percentual(v):
    m = re.match(r'(\d+(?:[,.]\d+)?)', v or '')
    return float(m[1].replace(',', '.')) if m else None


def _nivel(v):
    m = re.match(r'f[áa]cil|m[ée]dio|dif[íi]cil', v or '', re.I)
    return sem_acento(m[0]).lower() if m else None


def ler(caminho):
    """Devolve (comentarios, classificacoes), listas de dict."""
    linhas = sorted(linhas_pdf(caminho), key=lambda l: (l['p'], round(l['y']), l['x']))
    rodape = _rodape(linhas)
    cabecalho = {}
    for l in linhas:
        if _cabecalho(l):
            cabecalho[l['p']] = (cabecalho.get(l['p'], '') + ' ' + l['t']).strip()

    conteudo = [l for l in linhas if not _cabecalho(l) and l['y'] < rodape]
    blocos, atual, rotulo = [], None, None
    for i, l in enumerate(conteudo):
        n = _rotulo(l)
        if n is not None:
            rotulo = dict(numero=n or _numero_perto(l, linhas), pagina=l['p'])
            atual = None
            continue
        t = _norm(l['t'])
        if t.startswith('CONTINUACAO DO COMENTARIO'):
            continue
        titulo = re.match(r'COMENTARIO(?: DA QUESTAO\s*(\d{1,2}))?$', t)
        if titulo and atual is not None:
            # Título repetido: é continuação do mesmo comentário (na página seguinte ou logo abaixo do primeiro
            # campo), a não ser que traga uma nova classificação quando o bloco já tem uma. Nesse caso é um
            # comentário sem rótulo de questão (ex.: o da Redação, depois da última questão).
            seguinte = conteudo[i + 1]['t'] if i + 1 < len(conteudo) else ''
            if not (CLASSIFICACAO.match(seguinte) and any(CLASSIFICACAO.match(x) for x in atual['linhas'][1:])):
                continue
            rotulo = None
        if titulo or (atual is None and rotulo and CAMPOS.match(l['t'])):
            atual = dict(rotulo=rotulo, numero_no_comentario=int(titulo[1]) if titulo and titulo[1] else None,
                         pagina=l['p'], linhas=[])
            blocos.append(atual)
            if titulo:
                continue
        if atual is not None:
            atual['linhas'].append(l['t'])

    comentarios, classificacoes = [], []
    for b in blocos:
        rot = b['rotulo'] or {}
        cab = _norm(cabecalho.get(rot.get('pagina', b['pagina']), ''))
        idioma = next((v for k, v in IDIOMAS.items() if k in cab), None)
        texto, campos = _campos(' '.join(b['linhas']))
        questao = rot.get('numero') or b['numero_no_comentario']
        if any((c['questao'], c['idioma'], c['texto']) == (questao, idioma, texto) for c in comentarios):
            continue  # o PDF repete a página do comentário (2019-2, questão 32)
        valor = {c: v for c, o, v in campos if o == 1 and v}
        # Nos anos recentes o comentário segue o objetivo sem rótulo próprio: o objetivo vai até o fim da 1ª frase.
        objetivo = re.match(r'.*?\.(?=\s+[A-ZÀ-Ú]|$)', valor.get('objetivo', ''))
        comentarios.append(dict(
            questao=questao, idioma=idioma, pagina=b['pagina'] + 1,
            questao_no_comentario=b['numero_no_comentario'], cabecalho=cabecalho.get(rot.get('pagina', b['pagina'])),
            gabarito=(re.match(r'[A-D]\b|ANULADA', valor.get('gabarito', '').upper()) or [None])[0],
            percentual_acertos=_percentual(valor.get('percentual')), nivel=_nivel(valor.get('nivel')),
            objetivo=objetivo[0] if objetivo else valor.get('objetivo'), texto=texto))
        for i, c in enumerate(_classificacoes(campos), 1):
            classificacoes.append(dict(questao=questao, idioma=idioma, ordem=i, **c))
    return comentarios, classificacoes


def _classificacoes(campos):
    """Liga cada subitem ao item mais recente antes dele; item sem subitem vira classificação só de item.

    A numeração dos rótulos ("Subitem do programa 2") não é confiável nos PDFs (há "Item 1 ... Subitem 2" e um só
    item com vários subitens numerados), por isso vale a posição. O eixo é o de mesmo número do item, se houver;
    senão, o último eixo antes do item.
    """
    out, eixos, eixo, atual = [], {}, None, None
    for campo, ordem, valor in campos:
        if campo in ('objetivo', 'comentario', 'gabarito', 'percentual', 'nivel'):
            break
        if not valor:
            continue
        if campo == 'eixo':
            eixos[ordem], eixo = valor, valor
        elif campo == 'item':
            if atual and not atual['tem_subitem']:
                out.append(dict(eixo=atual['eixo'], item=atual['item'], subitem=None))
            atual = dict(item=valor, eixo=eixos.get(ordem, eixo), tem_subitem=False)
        elif campo == 'subitem':
            out.append(dict(eixo=atual['eixo'] if atual else eixo, item=atual and atual['item'], subitem=valor))
            if atual:
                atual['tem_subitem'] = True
    if atual and not atual['tem_subitem']:
        out.append(dict(eixo=atual['eixo'], item=atual['item'], subitem=None))
    return out
