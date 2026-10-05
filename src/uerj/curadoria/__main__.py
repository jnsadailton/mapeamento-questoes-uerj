"""Sugere ligações para os textos pendentes: uv run python -m uerj.curadoria

Lê o modelo `pendencias` do warehouse (rode o dbt antes), compara cada texto com os subitens canônicos e com os textos
já presentes no dicionário e grava data/curadoria/sugestoes.csv, no formato de dbt/seeds/dicionario_conteudo.csv.
As sugestões precisam de revisão antes de entrar no dicionário.
"""
import csv
import difflib
from collections import defaultdict
from pathlib import Path

import duckdb

from ..ingestao.catalogo import RAIZ
from . import normalizar

SEEDS = RAIZ / 'dbt' / 'seeds'
WAREHOUSE = RAIZ / 'data' / 'warehouse' / 'uerj.duckdb'
SAIDA = RAIZ / 'data' / 'curadoria' / 'sugestoes.csv'


def pontuacao(parte, alvo):
    """1 = igual; 0,95 = quase igual (erro de digitação); 0,9 = parte contida no alvo; 0 = sem relação."""
    if parte == alvo:
        return 1.0
    if difflib.SequenceMatcher(None, parte, alvo).ratio() >= 0.9:
        return 0.95
    if f' {parte} ' in f' {alvo} ':
        return 0.9
    a, b = set(parte.split()), set(alvo.split())
    return 0.8 if a and b and len(a & b) / len(a | b) >= 0.75 else 0.0


def sugerir(pendencias, base, dicionario):
    """Para cada pendência (item, subitem), os conteúdos canônicos mais parecidos dentro do item correspondente."""
    itens = defaultdict(set)      # item normalizado -> ids de item canônico
    textos = defaultdict(set)     # id de item -> {(subitem normalizado, id do subitem)}
    for b in base:
        id_item = b['id_subitem'].rsplit('.', 1)[0]
        itens[normalizar(b['item'])].add(id_item)
        textos[id_item].add((normalizar(b['subitem']), b['id_subitem']))
    for d in dicionario:
        id_item = '.'.join(d['id_conteudo'].split('.')[:3])
        itens[normalizar(d['item_texto'])].add(id_item)
        textos[id_item].add((normalizar(d['subitem_texto']), d['id_conteudo']))
    nomes = {b['id_subitem']: b['subitem'] for b in base}

    for item, subitem in pendencias:
        ni, ns = normalizar(item), normalizar(subitem)
        perto = difflib.get_close_matches(ni, list(itens), 1, 0.8)
        candidatos = {}
        for id_item in itens.get(ni) or (itens[perto[0]] if perto else set()):
            for texto, id_conteudo in textos[id_item]:
                candidatos[id_conteudo] = max(candidatos.get(id_conteudo, 0), pontuacao(ns, texto))
        melhores = sorted(((p, i) for i, p in candidatos.items() if p > 0), reverse=True)[:3]
        yield dict(item_texto=item, subitem_texto=subitem,
                   id_conteudo=melhores[0][1] if melhores else '',
                   origem='comentario', metodo='manual',
                   justificativa='REVISAR: ' + '; '.join(f'{i} {nomes.get(i, "")} ({p:.2f})' for p, i in melhores))


def main():
    with duckdb.connect(str(WAREHOUSE), read_only=True) as con:
        pendencias = con.sql('select distinct item_texto, subitem_texto from pendencias').fetchall()
    if not pendencias:
        print('Nenhuma pendência: todos os textos têm ligação no dicionário.')
        return
    ler = lambda nome: list(csv.DictReader(open(SEEDS / nome, encoding='utf-8')))
    linhas = list(sugerir(pendencias, ler('conteudo_base.csv'), ler('dicionario_conteudo.csv')))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SAIDA, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(linhas[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(linhas)
    print(f'{len(linhas)} pendências; sugestões em {SAIDA}. Revise e copie para dbt/seeds/dicionario_conteudo.csv.')


if __name__ == '__main__':
    main()
