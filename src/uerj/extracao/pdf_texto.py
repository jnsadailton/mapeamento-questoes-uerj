"""Leitura das linhas de um PDF com posição na página.

Alguns gabaritos comentados (2026 e 2027) usam uma fonte Cambria sem tabela de caracteres: o texto sai como números de
glifo. O arquivo glifos_cambria.json traduz esses números de volta para letras. Nos de 2026, a Cambria desenha alguns
acentos como glifo à parte, que sai como um espaço de largura zero depois da letra ("me dio", "relaço es"); o id do glifo
diz qual é o acento, e ele é juntado de volta à letra.
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


# id do glifo do acento solto (Cambria dos comentados de 2026) -> acento combinante
_ACENTOS_SOLTOS = {432: 0x300, 436: 0x301, 437: 0x301, 440: 0x302, 449: 0x303}  # crase, agudo, circunflexo, til
_MARCA = 0xE000  # o acento solto entra no texto como caractere de uso privado (0xE000 + código do acento)


def _acentos_soltos(pg):
    """Posição (origem) de cada espaço de largura zero que é glifo de acento -> marca do acento."""
    return {(round(o[0], 1), round(o[1], 1)): chr(_MARCA + _ACENTOS_SOLTOS[g])
            for sp in pg.get_texttrace() if 'cambria' in sp['font'].lower()
            for u, g, o, bb in sp['chars'] if u == 32 and bb[2] - bb[0] < 0.5 and g in _ACENTOS_SOLTOS}


def _juntar_acentos(t):
    """Letra + acento solto -> letra acentuada. O acento sobra quando a letra já tem um ("í" + agudo)."""
    def juntar(m):
        junto = unicodedata.normalize('NFC', m[1] + chr(ord(m[2]) - _MARCA))
        return junto if m[1] and len(junto) == 1 else m[1]
    return re.sub(r'(.?)([-])', juntar, t)


def _normalizar(t):
    # "ϐ" desenha só o "f" da ligadura (o "i" vem em seguida: "diϐiculdade", "conϐlito"), "í" perdido em algumas
    # fontes e espaços estranhos
    t = _juntar_acentos(t).replace('ϐ', 'f').replace('ı́', 'í').replace('́', 'í').replace('', 'i')
    t = unicodedata.normalize('NFC', t).replace('́', 'í')
    return re.sub('[ \t Â]+', ' ', t).strip()


def linhas_pdf(caminho):
    """Devolve as linhas do PDF: dict(p=página a partir de 0, x, y, x1, y1, t=texto)."""
    out = []
    for pi, pg in enumerate(pymupdf.open(caminho)):
        acentos = None
        for b in pg.get_text('rawdict')['blocks']:
            for l in b.get('lines', []):
                partes = []
                for s in l['spans']:
                    cs, chars = [], s['chars']
                    for i, c in enumerate(chars):
                        if c['c'] == ' ' and c['bbox'][2] - c['bbox'][0] < 0.5 and 'cambria' in s['font'].lower():
                            acentos = _acentos_soltos(pg) if acentos is None else acentos
                            acento = acentos.get((round(c['origin'][0], 1), round(c['origin'][1], 1)))
                            if acento is None:
                                cs.append(' ')
                                continue
                            cs.append(acento)
                            # o acento às vezes ocupa o lugar do espaço ("é o amor"): vão de palavra até a letra seguinte
                            if 0 < i < len(chars) - 1 and chars[i + 1]['bbox'][0] - chars[i - 1]['bbox'][2] > 1.5:
                                cs.append(' ')
                        else:
                            cs.append(c['c'])
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
