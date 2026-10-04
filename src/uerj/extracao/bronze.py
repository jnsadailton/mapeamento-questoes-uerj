"""Camada bronze: roda os parsers sobre os PDFs de data/raw/ e grava uma tabela Parquet por tipo de registro."""
import argparse
import time
from datetime import date
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from ..ingestao import manifesto
from ..ingestao.obter import DESTINO as RAW
from . import comentado, conteudo, gabarito, prova

BRONZE = manifesto.RAIZ / 'data' / 'bronze'

texto, inteiro, real = pa.string(), pa.int32(), pa.float64()
ESQUEMAS = {
    'gabarito': pa.schema([('exame', texto), ('questao', inteiro), ('idioma', texto), ('resposta', texto),
                           ('data_aplicacao', pa.date32())]),
    'comentario': pa.schema([('exame', texto), ('questao', inteiro), ('idioma', texto), ('pagina', inteiro),
                             ('questao_no_comentario', inteiro), ('cabecalho', texto), ('gabarito', texto),
                             ('percentual_acertos', real), ('nivel', texto), ('objetivo', texto), ('texto', texto)]),
    'classificacao': pa.schema([('exame', texto), ('questao', inteiro), ('idioma', texto), ('ordem', inteiro),
                                ('eixo', texto), ('item', texto), ('subitem', texto)]),
    'conteudo_programatico': pa.schema([('exame', texto), ('area', texto), ('eixo', texto), ('item', texto),
                                        ('subitem', texto), ('ordem_item', inteiro), ('ordem_subitem', inteiro),
                                        ('pagina', inteiro)]),
    'prova': pa.schema([('exame', texto), ('questao', inteiro), ('idioma', texto), ('pagina', inteiro)]),
}


def extrair_exame(exame, raw=RAW):
    """Roda os parsers de um exame e devolve {tabela: [linhas]}."""
    pasta = Path(raw) / exame
    data, gab = gabarito.ler(pasta / f'{exame}_gabarito.pdf')
    com, cla = comentado.ler(pasta / f'{exame}_gabarito_comentado.pdf')
    cont = conteudo.ler(pasta / f'{exame}_conteudo_programatico.pdf')
    pro = prova.ler(pasta / f'{exame}_prova.pdf')
    data = date.fromisoformat(data) if data else None
    return {
        'gabarito': [dict(exame=exame, data_aplicacao=data, **g) for g in gab],
        'comentario': [dict(exame=exame, **c) for c in com],
        'classificacao': [dict(exame=exame, **c) for c in cla],
        'conteudo_programatico': [dict(exame=exame, **c) for c in cont],
        'prova': [dict(exame=exame, **p) for p in pro],
    }


def gravar(tabelas, destino=BRONZE):
    Path(destino).mkdir(parents=True, exist_ok=True)
    for nome, linhas in tabelas.items():
        pq.write_table(pa.Table.from_pylist(linhas, schema=ESQUEMAS[nome]), Path(destino) / f'{nome}.parquet')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw', default=RAW)
    p.add_argument('--destino', default=BRONZE)
    a = p.parse_args()
    exames = sorted({d.exame for d in manifesto.carregar()})
    faltando = [e for e in exames if not (Path(a.raw) / e).is_dir()]
    if faltando:
        raise SystemExit(f'Faltam PDFs em {a.raw} para {faltando}. Rode antes: uv run python -m uerj.ingestao')

    inicio = time.time()
    tabelas = {nome: [] for nome in ESQUEMAS}
    with ProcessPoolExecutor() as ex:
        for resultado in ex.map(extrair_exame, exames, [a.raw] * len(exames)):
            for nome, linhas in resultado.items():
                tabelas[nome].extend(linhas)
    gravar(tabelas, a.destino)
    print(f'{len(exames)} exames extraídos em {time.time() - inicio:.0f}s para {a.destino}')
    for nome, linhas in tabelas.items():
        print(f'  {nome}: {len(linhas)} linhas')

