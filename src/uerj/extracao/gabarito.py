"""Leitura dos gabaritos oficiais: uma linha por questão (e por idioma no bloco de língua estrangeira).

Há duas famílias de layout. De 2016 a 2023 cada número vem seguido da resposta na mesma linha ("17  C"). De 2024 em
diante há uma linha de números e, logo abaixo, uma linha de respostas alinhadas a eles. Por isso a resposta de cada
número é procurada primeiro à direita, na mesma linha, e depois logo abaixo, na mesma coluna.

"ANULADA" aparece inteira, com caixa variada ("Anulada") ou partida em dois pedaços ("LADA ANU", em 2026-1).
"""
import re

import pymupdf

from .pdf_texto import sem_acento

IDIOMAS = {'ESPANHOL': 'ES', 'FRANCES': 'FR', 'INGLES': 'EN'}


def _palavras(caminho):
    pg = pymupdf.open(caminho)[0]
    return [dict(x0=w[0], y0=w[1], x1=w[2], y1=w[3], t=w[4]) for w in pg.get_text('words')], pg.get_text()


def _meio_y(w):
    return (w['y0'] + w['y1']) / 2


def _anulada(t):
    t = sem_acento(t).upper()
    return len(t) >= 3 and t in 'ANULADA'


def _resposta(n, palavras, numeros):
    """Resposta do número n: à direita na mesma linha ou, se não houver, logo abaixo na mesma coluna."""
    def a_direita(w):
        return abs(_meio_y(w) - _meio_y(n)) < 4 and w['x0'] > n['x1']
    proximo = min((w['x0'] for w in numeros if a_direita(w)), default=float('inf'))
    direita = sorted((w for w in palavras if a_direita(w) and w['x0'] < proximo), key=lambda w: w['x0'])
    if direita:
        return direita[0]
    meio_x = (n['x0'] + n['x1']) / 2
    abaixo = [w for w in palavras
              if 0 < _meio_y(w) - _meio_y(n) < 30 and w['x0'] - 3 <= meio_x <= w['x1'] + 3]
    return min(abaixo, key=lambda w: _meio_y(w), default=None)


def _idioma(n, cabecalhos):
    """Cabeçalho de idioma mais próximo acima do número e, entre os da mesma altura, o mais à direita sem passar dele."""
    acima = [c for c in cabecalhos if c['y1'] <= n['y0'] + 2 and c['x0'] <= n['x0'] + 15]
    if not acima:
        return None
    c = min(acima, key=lambda c: (round((n['y0'] - c['y1']) / 10), -c['x0']))
    return IDIOMAS[sem_acento(c['t']).upper()]


def ler(caminho):
    """Devolve (data_aplicacao 'AAAA-MM-DD', lista de dict(questao, idioma, resposta))."""
    palavras, texto = _palavras(caminho)
    d = re.search(r'(\d{2})/(\d{2})/(\d{4})', texto)
    data = f'{d[3]}-{d[2]}-{d[1]}' if d else None

    numeros = [w for w in palavras if re.fullmatch(r'\d{1,2}', w['t']) and 1 <= int(w['t']) <= 60]
    respostas = [w for w in palavras if re.fullmatch(r'[A-D]', w['t']) or _anulada(w['t'])]
    cabecalhos = [w for w in palavras if sem_acento(w['t']).upper() in IDIOMAS]
    repetidos = {t for t in {w['t'] for w in numeros} if sum(w['t'] == t for w in numeros) > 1}

    linhas = []
    for n in numeros:
        r = _resposta(n, respostas, numeros)
        if r is None:
            raise ValueError(f'{caminho}: questão {n["t"]} sem resposta')
        linhas.append(dict(questao=int(n['t']),
                           idioma=_idioma(n, cabecalhos) if n['t'] in repetidos else None,
                           resposta='ANULADA' if _anulada(r['t']) else r['t']))
    linhas.sort(key=lambda l: (l['questao'], l['idioma'] or ''))
    return data, linhas
