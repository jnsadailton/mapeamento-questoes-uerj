"""Leitura do conteúdo programático do edital: um registro por subitem (ou por item, quando não há subitens).

Estrutura do anexo: cada área (ou disciplina, no Exame Único) começa com um título seguido de "ORIENTAÇÃO GERAL" e um
texto corrido. Depois vêm os eixos, em linhas sem marcador, e abaixo de cada eixo os itens, um por marcador:
"• Item: subitem; subitem; ...". O item pode continuar nas linhas seguintes, com recuo maior.
"""
import re

from .pdf_texto import linhas_pdf, sem_acento

MARCADOR = re.compile(r'^[•▪●]\s*')
# Títulos de área (Exames de Qualificação) e de disciplina (Exame Único). Em geral vêm antes de "ORIENTAÇÃO GERAL",
# mas a Biologia de 2023 vem sem ela.
AREAS = re.compile(r'LINGUAGENS|MATEMATICA|CIENCIAS DA NATUREZA|CIENCIAS HUMANAS|BIOLOGIA|FISICA|QUIMICA|GEOGRAFIA'
                   r'|HISTORIA|LINGUA ESTRANGEIRA|LINGUA PORTUGUESA E LITERATURAS?')


def _norm(t):
    return sem_acento(t).upper().strip()


def _descartar(l):
    """Título do anexo, rodapé e número de página."""
    t = _norm(l['t'])
    return (re.fullmatch(r'\d{1,2}|ANEXO \d', t) or 'MANUAL DO CANDIDATO' in t
            or re.fullmatch(r'CONTEUDOS (BASICOS|PROGRAMATICOS)', t))


def _linhas(caminho):
    """Linhas do PDF, juntando os fragmentos que estão na mesma altura (marcador solto, texto após um expoente).

    Em 2016, "g.L-1" quebra a linha: o trecho depois do expoente fica um pouco mais alto e, ordenado só por y,
    iria parar antes do item a que pertence.
    """
    linhas = []
    for l in sorted(linhas_pdf(caminho), key=lambda l: (l['p'], l['y'], l['x'])):
        meio = (l['y'] + l['y1']) / 2
        atual = linhas[-1] if linhas else None
        if atual and atual['p'] == l['p'] and atual['y'] <= meio <= atual['y1']:
            atual['partes'].append(l)
        else:
            linhas.append(dict(p=l['p'], y=l['y'], y1=l['y1'], partes=[l]))
    for r in linhas:
        r['partes'].sort(key=lambda l: l['x'])
        r['x'] = r['partes'][0]['x']
        r['t'] = ' '.join(l['t'] for l in r['partes'])
    return linhas


def _item(texto):
    """Separa "Item: sub1; sub2" em (item, [subitens])."""
    nome, _, resto = texto.partition(':')
    subitens = [s.strip().rstrip('.').strip() for s in resto.split(';')] if resto else []
    return nome.strip().rstrip('.'), [s for s in subitens if s]


def ler(caminho):
    """Devolve lista de dict(area, eixo, item, subitem, ordem_item, ordem_subitem, pagina)."""
    linhas = [l for l in _linhas(caminho) if not _descartar(l)]
    area = eixo = None
    itens = []  # (area, eixo, pagina, x do marcador, [linhas])
    atual = None
    for i, l in enumerate(linhas):
        seguinte = linhas[i + 1]['t'] if i + 1 < len(linhas) else ''
        t = l['t']
        if _norm(seguinte) == 'ORIENTACAO GERAL' or AREAS.fullmatch(_norm(t)):
            area, eixo, atual = t.strip(), None, None
        elif MARCADOR.match(t) and ':' not in t and MARCADOR.match(seguinte):
            # Título de eixo grafado como item ("• Aspectos literários", Língua Portuguesa de 2021)
            eixo, atual = MARCADOR.sub('', t).strip(), None
        elif MARCADOR.match(t):
            atual = dict(area=area, eixo=eixo, pagina=l['p'] + 1, x=l['x'], linhas=[MARCADOR.sub('', t)])
            itens.append(atual)
        elif atual and l['x'] > atual['x'] + 3:
            atual['linhas'].append(t)
        elif MARCADOR.match(seguinte):
            eixo, atual = t.strip(), None
        else:
            atual = None  # texto corrido (orientação geral, observações)

    out = []
    for n, it in enumerate(itens, 1):
        nome, subitens = _item(' '.join(it['linhas']))
        base = dict(area=it['area'], eixo=it['eixo'], item=nome, ordem_item=n, pagina=it['pagina'])
        for k, s in enumerate(subitens or [None], 1):
            out.append(dict(base, subitem=s, ordem_subitem=k if s else None))
    return out
