"""Ingestão dos PDFs: uv run python -m uerj.ingestao [--exame AAAA-N ...] [--somente-repositorio]"""
import argparse
import collections
import logging

from . import manifesto
from .obter import DESTINO, FONTES, obter_todos


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exame', nargs='*', help='só estes exames (padrão: todos)')
    p.add_argument('--somente-repositorio', action='store_true',
                   help='não acessa a internet; usa só a cópia versionada em fontes/pdfs/')
    p.add_argument('--destino', default=DESTINO)
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    docs = manifesto.carregar()
    if a.exame:
        docs = [d for d in docs if d.exame in a.exame]
    fontes = ('repositorio',) if a.somente_repositorio else FONTES
    provs = obter_todos(docs, a.destino, fontes=fontes)

    print(f'{len(provs)} documentos em {a.destino}')
    for fonte, n in sorted(collections.Counter(p.fonte for p in provs).items()):
        print(f'  {fonte}: {n}')
    divergentes = [p for p in provs if 'sha256 diferente' in p.avisos]
    for p in divergentes:
        print(f'ATENÇÃO {p.arquivo}: uma fonte devolveu arquivo diferente do manifesto '
              f'(gabarito retificado?). Confira e, se for o caso, atualize a cópia e o manifesto.\n  {p.avisos}')


if __name__ == '__main__':
    main()
