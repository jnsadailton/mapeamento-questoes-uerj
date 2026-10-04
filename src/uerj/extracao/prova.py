"""Página de cada questão no caderno de prova, para o site abrir o PDF direto na questão.

O número de cada questão vem sozinho, em corpo grande (27 a 60 pt, conforme o ano), na margem esquerda. Ele é o número
de um ou dois dígitos mais frequente entre os de corpo grande; a capa (página 1) fica de fora porque traz o número do
exame no mesmo corpo. No bloco de língua estrangeira, cada número aparece três vezes, sempre na ordem espanhol,
francês e inglês.
"""
import re
from collections import Counter

import pymupdf

IDIOMAS = ('ES', 'FR', 'EN')


def _numeros_grandes(caminho):
    """(página a partir de 1, y, número, corpo) de cada número de um ou dois dígitos em corpo de 16 pt ou mais."""
    achados = []
    for pno, pg in enumerate(pymupdf.open(caminho)):
        if pno == 0:
            continue
        for bloco in pg.get_text('dict')['blocks']:
            for linha in bloco.get('lines', []):
                for s in linha['spans']:
                    t = s['text'].strip()
                    if re.fullmatch(r'\d{1,2}', t) and s['size'] >= 16:
                        achados.append((pno + 1, s['bbox'][1], int(t), s['size']))
    return sorted(achados)


def ler(caminho):
    """Devolve lista de dict(questao, idioma, pagina), na ordem do caderno."""
    achados = _numeros_grandes(caminho)
    if not achados:
        raise ValueError(f'{caminho}: nenhum número de questão encontrado')
    corpo = Counter(round(a[3]) for a in achados).most_common(1)[0][0]
    rotulos = [a for a in achados if abs(a[3] - corpo) <= 0.06 * corpo]
    vezes = Counter(r[2] for r in rotulos)
    vistos = Counter()
    linhas = []
    for pagina, _, n, _ in rotulos:
        idioma = None
        if vezes[n] > 1:
            idioma = IDIOMAS[vistos[n]]
            vistos[n] += 1
        linhas.append(dict(questao=n, idioma=idioma, pagina=pagina))
    return linhas
