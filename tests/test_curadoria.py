"""Testes dos seeds de curadoria (dbt/seeds/) contra a saída dos parsers."""
import csv
import re
from collections import defaultdict

import duckdb
import pytest

from uerj.curadoria import normalizar
from uerj.curadoria.__main__ import sugerir
from uerj.ingestao.catalogo import EXAMES, RAIZ

SEEDS = RAIZ / 'dbt' / 'seeds'
TIPOS = {'classificacao_manual', 'transcricao', 'complemento'}


def ler(nome):
    with open(SEEDS / nome, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def chave(exame, questao, idioma):
    return exame, int(questao), idioma or ''


@pytest.fixture(scope='module')
def correcoes():
    return ler('correcoes.csv')


@pytest.fixture(scope='module')
def eixos():
    return ler('eixos_atribuidos.csv')


def test_correcoes_bem_formadas(correcoes):
    assert all(r['tipo'] in TIPOS and r['justificativa'].strip() for r in correcoes)
    vistos = set()
    for r in correcoes:
        k = (*chave(r['exame'], r['questao'], r['idioma']), int(r['ordem']))
        assert k not in vistos, k
        vistos.add(k)
        assert r['eixo'] and r['item'] and r['subitem'], k
        assert r['nivel'] in ('', 'facil', 'medio', 'dificil')
        assert r['percentual_acertos'] == '' or 0 <= float(r['percentual_acertos']) <= 100
    # quem completa ou estima algo precisa de observação pública (exibida no site)
    assert all(r['observacao'].strip() for r in correcoes if r['tipo'] == 'classificacao_manual')


def test_classificacoes_completas_depois_da_curadoria(bronze, correcoes, eixos):
    """Aplicadas as correções e os eixos atribuídos, toda classificação tem eixo, item e subitem."""
    corrigidas = {chave(r['exame'], r['questao'], r['idioma']) for r in correcoes}
    eixo_de = {(*chave(r['exame'], r['questao'], r['idioma']), r['item']): r['eixo'] for r in eixos}
    usados, incompletas = set(), []
    for exame in EXAMES:
        for c in bronze[exame]['classificacao']:
            if c['questao'] is None:  # comentário da Redação (2021-1), fora do escopo
                continue
            k = chave(exame, c['questao'], c['idioma'])
            if k in corrigidas:
                continue
            eixo = c['eixo']
            if not eixo and (*k, c['item']) in eixo_de:
                eixo = eixo_de[(*k, c['item'])]
                usados.add((*k, c['item']))
            if not (eixo and c['item'] and c['subitem']):
                incompletas.append((*k, c['ordem']))
    assert incompletas == []
    assert usados == set(eixo_de), 'eixo atribuído que não corresponde a nenhuma classificação sem eixo'


def test_toda_questao_nao_anulada_tem_classificacao(bronze, correcoes):
    corrigidas = {chave(r['exame'], r['questao'], r['idioma']) for r in correcoes}
    for exame in EXAMES:
        classificadas = {chave(exame, c['questao'], c['idioma']) for c in bronze[exame]['classificacao']
                         if c['questao'] is not None}
        for g in bronze[exame]['gabarito']:
            k = chave(exame, g['questao'], g['idioma'])
            if g['resposta'] != 'ANULADA':
                assert k in classificadas or k in corrigidas, k


def test_correcao_nao_aponta_para_questao_inexistente(bronze, correcoes):
    existentes = defaultdict(set)
    for exame in EXAMES:
        existentes[exame] = {chave(exame, g['questao'], g['idioma'])[1:] for g in bronze[exame]['gabarito']}
    for r in correcoes:
        assert chave(r['exame'], r['questao'], r['idioma'])[1:] in existentes[r['exame']], r


def test_normalizacao_python_igual_a_macro_do_dbt():
    """As chaves do dicionário são calculadas no dbt; a curadoria em Python precisa chegar ao mesmo texto."""
    macro = (RAIZ / 'dbt' / 'macros' / 'normalizar_texto.sql').read_text(encoding='utf-8')
    corpo = re.search(r'macro normalizar_texto\(coluna\) -%\}(.*?)\{%- endmacro', macro, re.S)[1]
    textos = sorted({t for r in ler('dicionario_conteudo.csv') for t in (r['item_texto'], r['subitem_texto'])})
    textos += ['uniforme- mente variado', 'Ação, Reação!', 'força-peso', '']
    con = duckdb.connect()
    con.execute('create table t (texto varchar)')
    con.executemany('insert into t values (?)', [[t] for t in textos])
    sql = dict(con.sql(f"select texto, {corpo.replace('{{ coluna }}', 'texto')} from t").fetchall())
    diferentes = [t for t in textos if sql[t] != normalizar(t)]
    assert diferentes == []


def test_sugestao_para_texto_novo():
    base = ler('conteudo_base.csv')
    s = next(sugerir([('Procedimentos de coesão e coerência', 'anáforas')], base, ler('dicionario_conteudo.csv')))
    assert s['id_conteudo'] == next(b['id_subitem'] for b in base if b['subitem'] == 'anáfora, catáfora, dêixis')
