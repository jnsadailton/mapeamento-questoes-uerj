"""Leitura das linhas de um PDF com posição na página.

Alguns gabaritos comentados (2026 e 2027) usam uma fonte Cambria sem tabela de caracteres: o texto sai como números de
glifo. O arquivo glifos_cambria.json traduz esses números de volta para letras.
"""
import json, os, re, unicodedata
import pymupdf

_GLIFOS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glifos_cambria.json'), encoding='utf-8'))


def sem_acento(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))


def _mapa(fonte):
    f = fonte.lower()
    estilo = ('bold' if 'bold' in f else '') + ('italic' if 'italic' in f else '')
    return _GLIFOS.get(estilo or 'regular', _GLIFOS['regular'])


def _codificado_por_glifo(chars):
    return any(ord(c) < 0x20 or 0x7f <= ord(c) <= 0x9f or 0x1e1 <= ord(c) <= 0x1e6 for c in chars)


def _normalizar(t):
    # ligadura "fi", "í" perdido em algumas fontes e espaços estranhos
    t = t.replace('ϐ', 'fi').replace('ı́', 'í').replace('́', 'í').replace('', 'i')
    t = unicodedata.normalize('NFC', t).replace('́', 'í')
    return re.sub('[ \t Â]+', ' ', t).strip()


def linhas_pdf(caminho):
    """Devolve as linhas do PDF: dict(p=página a partir de 0, x, y, x1, y1, t=texto)."""
    out = []
    for pi, pg in enumerate(pymupdf.open(caminho)):
        for b in pg.get_text('rawdict')['blocks']:
            for l in b.get('lines', []):
                partes = []
                for s in l['spans']:
                    cs = [c['c'] for c in s['chars']]
                    if 'cambria' in s['font'].lower() and _codificado_por_glifo(cs):
                        m = _mapa(s['font'])
                        partes.append(''.join(m.get(str(ord(c)), '') for c in cs))
                    else:
                        partes.append(''.join(cs))
                t = _normalizar(''.join(partes))
                if t:
                    x0, y0, x1, y1 = l['bbox']
                    out.append(dict(p=pi, x=x0, y=y0, x1=x1, y1=y1, t=t))
    return out
