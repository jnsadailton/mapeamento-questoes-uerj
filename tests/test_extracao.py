"""Testes dos parsers sobre a cópia versionada dos PDFs (fontes/pdfs/), com os casos especiais conhecidos."""
from collections import Counter, defaultdict

import pytest

from uerj.ingestao.manifesto import EXAMES

UNICO = {'2021-1', '2022-1', '2023-1'}
ANULADAS = {'2017-2': 35, '2023-1': 34, '2024-1': 29, '2024-2': 59, '2025-2': 38, '2026-1': 38, '2027-1': 29,
            '2027-2': 34}

# Lacunas da própria fonte, conferidas na imagem das páginas.
SEM_COMENTARIO = {('2024-2', 38, None)}  # o PDF passa da questão 37 para a 39
SEM_CLASSIFICACAO = {('2026-2', 32, None), ('2026-2', 34, None), ('2026-2', 42, None)}  # classificação em imagem
# Comentários sem rótulo de questão: o da Redação, depois da questão 60.
SEM_QUESTAO = {'2021-1': 1}
# Percentual de acertos ausente no PDF (além das anuladas).
SEM_PERCENTUAL = {'2021-1', '2024-2', '2027-2'}


def chave(r):
    return r['questao'], r['idioma']


# --- gabarito -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize('exame', EXAMES)
def test_gabarito_tem_60_questoes_e_lingua_estrangeira_em_tres_idiomas(bronze, exame):
    gab = bronze[exame]['gabarito']
    assert {g['questao'] for g in gab} == set(range(1, 61))
    idiomas = defaultdict(set)
    for g in gab:
        idiomas[g['questao']].add(g['idioma'])
    le = [q for q, i in idiomas.items() if i != {None}]
    assert all(idiomas[q] == {'ES', 'FR', 'EN'} for q in le)
    assert len(le) == (7 if exame in UNICO else 5)
    assert Counter(chave(g) for g in gab).most_common(1)[0][1] == 1


@pytest.mark.parametrize('exame', EXAMES)
def test_gabarito_respostas_e_anuladas(bronze, exame):
    gab = bronze[exame]['gabarito']
    assert {g['resposta'] for g in gab} <= {'A', 'B', 'C', 'D', 'ANULADA'}
    anuladas = {g['questao'] for g in gab if g['resposta'] == 'ANULADA'}
    assert anuladas == ({ANULADAS[exame]} if exame in ANULADAS else set())
    assert all(g['data_aplicacao'] for g in gab)


def test_gabarito_casos_de_layout(bronze):
    def resposta(exame, questao, idioma=None):
        return next(g['resposta'] for g in bronze[exame]['gabarito'] if chave(g) == (questao, idioma))
    assert resposta('2016-1', 17, 'ES') == 'C' and resposta('2016-1', 17, 'EN') == 'C'  # pares em colunas
    assert resposta('2021-1', 12, 'FR') == 'B' and resposta('2021-1', 12, 'EN') == 'A'  # idiomas lado a lado
    assert resposta('2024-1', 23, 'FR') == 'A' and resposta('2027-2', 27, 'EN') == 'A'  # grade
    assert resposta('2027-2', 33) == 'B'  # o 34 (anulada) fica fora da linha dos números
    assert str(bronze['2027-1']['gabarito'][0]['data_aplicacao']) == '2026-06-07'


# --- gabarito comentado ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize('exame', EXAMES)
def test_um_comentario_por_questao_e_idioma(bronze, exame):
    esperado = {chave(g) for g in bronze[exame]['gabarito']} - {(q, i) for e, q, i in SEM_COMENTARIO if e == exame}
    com = bronze[exame]['comentario']
    obtido = Counter(chave(c) for c in com if c['questao'] is not None)
    assert set(obtido) == esperado
    assert max(obtido.values()) == 1
    assert sum(c['questao'] is None for c in com) == SEM_QUESTAO.get(exame, 0)


@pytest.mark.parametrize('exame', EXAMES)
def test_todo_comentario_tem_classificacao(bronze, exame):
    com = {chave(c) for c in bronze[exame]['comentario'] if c['questao'] is not None}
    cla = {chave(c) for c in bronze[exame]['classificacao']}
    assert com - cla == {(q, i) for e, q, i in SEM_CLASSIFICACAO if e == exame}
    assert all(c['item'] or c['subitem'] for c in bronze[exame]['classificacao'])


@pytest.mark.parametrize('exame', EXAMES)
def test_percentual_de_acertos(bronze, exame):
    com = [c for c in bronze[exame]['comentario'] if c['questao'] is not None]
    percentuais = [c['percentual_acertos'] for c in com if c['percentual_acertos'] is not None]
    assert all(0 <= p <= 100 for p in percentuais)
    if exame in SEM_PERCENTUAL:
        assert not percentuais
    else:
        # só faltam os das anuladas, os casos em que o PDF não traz o campo (2020-2 e 2022-1) e os de texto
        # embaralhado (2026-2), que vêm de seeds/correcoes.csv
        assert len(percentuais) >= len(com) - {'2022-1': 12, '2026-2': 3}.get(exame, 2)


def test_nivel_de_dificuldade(bronze):
    """Todo comentário com percentual traz o nível, menos os casos em que o PDF não traz o campo ou o deixa vazio."""
    sem_nivel = {(e, c['questao'], c['idioma']) for e in EXAMES for c in bronze[e]['comentario']
                 if c['percentual_acertos'] is not None and c['nivel'] is None}
    assert sem_nivel == {
        ('2017-1', 50, None), ('2020-2', 5, None), ('2020-2', 20, None), ('2020-2', 24, 'EN'), ('2022-1', 34, None),
        ('2022-1', 39, None), ('2022-1', 54, None), ('2023-1', 24, None), ('2023-1', 41, None), ('2024-1', 24, 'FR'),
        ('2024-1', 45, None), ('2026-2', 23, 'ES'), ('2026-2', 60, None), ('2027-1', 27, 'FR')}


def test_comentado_casos_especiais(bronze):
    def comentario(exame, questao, idioma=None):
        return next(c for c in bronze[exame]['comentario'] if chave(c) == (questao, idioma))

    def classificacoes(exame, questao, idioma=None):
        return [c for c in bronze[exame]['classificacao'] if chave(c) == (questao, idioma)]

    # número errado no próprio comentário: vale o rótulo da questão
    assert comentario('2016-1', 44)['questao_no_comentario'] == 42
    # campos na mesma linha (2016) e glifos Cambria decodificados (2026-2027)
    assert classificacoes('2016-1', 1)[0]['subitem'].startswith('Quem enuncia')
    assert comentario('2027-1', 13)['percentual_acertos'] == 62.72
    # "Item 1 / Subitem 2 / Item 1 / Subitem 2": ligação pela posição
    assert [c['subitem'] for c in classificacoes('2020-2', 23, 'EN')] == [
        'reformulação, paráfrase.', 'comparação; generalização.', 'metáfora.']
    # um item com vários subitens numerados
    assert {c['item'] for c in classificacoes('2023-1', 20)} == {'círculo trigonométrico.'}
    assert len(classificacoes('2023-1', 20)) == 3
    # percentual sem o símbolo de %
    assert comentario('2019-1', 1)['percentual_acertos'] == 72.46
    # itens e subitens listados em bloco ("Item 1, Item 2, Subitem 1, Subitem 2"): ligação pelo número
    assert [(c['item'], c['subitem']) for c in classificacoes('2018-1', 5)] == [
        ('sucessões.', 'por recorrência.'), ('figuras no plano.', 'relações métricas.')]
    # linhas de eixo e item repetidas no PDF não geram classificação duplicada
    assert len(classificacoes('2022-1', 15, 'ES')) == 1
    # segunda classificação depois do primeiro "Objetivo"
    assert [c['item'] for c in classificacoes('2024-2', 23, 'ES')] == [
        'métodos de argumentação.', 'formas de articulação de ideias.']
    # rótulo com erro de digitação ("Eixo interdisplinar")
    assert classificacoes('2024-1', 27, 'EN')[0]['eixo'] == 'construção do texto.'
    # texto da questão seguinte não vaza para o fim do comentário
    assert comentario('2024-1', 11)['texto'].endswith('Nível de dificuldade: fácil.')
    assert comentario('2024-1', 11)['nivel'] == 'facil'
    # 2026: ligadura "ϐ" (só o "f") e acentos desenhados à parte, que saem como espaço de largura zero
    assert comentario('2026-1', 9)['nivel'] == 'medio'
    assert 'referência produz um efeito de polissemia, isto é, de múltiplo sentido' in comentario('2026-1', 2)['texto']
    assert 'último quadrinho – é o amor' in comentario('2026-1', 9)['texto']
    assert not any('fii' in c['texto'] or 'Ní vel' in c['texto']
                   for e in ('2026-1', '2026-2') for c in bronze[e]['comentario'])


# --- conteúdo programático ------------------------------------------------------------------------------------------

@pytest.mark.parametrize('exame', EXAMES)
def test_conteudo_programatico(bronze, exame):
    cont = bronze[exame]['conteudo_programatico']
    assert len({c['area'] for c in cont}) == (8 if exame in UNICO else 4)
    assert all(c['area'] and c['eixo'] and c['item'] for c in cont)
    assert len({c['ordem_item'] for c in cont}) > 60


def test_conteudo_igual_nos_dois_exames_do_ano(bronze):
    def conteudo(e):
        return [(c['area'], c['eixo'], c['item'], c['subitem']) for c in bronze[e]['conteudo_programatico']]
    for ano in [2016, 2017, 2018, 2019, 2020, 2025, 2026, 2027]:
        assert conteudo(f'{ano}-1') == conteudo(f'{ano}-2')


def test_conteudo_titulo_de_eixo_grafado_como_item(bronze):
    # o edital de 2021 escreve "• Aspectos literários" (com marcador de item) na Língua Portuguesa
    cont = [c for c in bronze['2021-1']['conteudo_programatico'] if c['item'] == 'Elementos da narrativa'
            and 'Portuguesa' in c['area']]
    assert {c['eixo'] for c in cont} == {'Aspectos literários'}
    assert all(c['subitem'] for c in bronze['2021-1']['conteudo_programatico'])


def test_conteudo_subitens_separados_por_ponto_e_virgula(bronze):
    subitens = [c['subitem'] for c in bronze['2016-1']['conteudo_programatico']
                if c['item'] == 'Perspectivas enunciativas']
    assert subitens == ['quem enuncia, a quem enuncia, espaço, tempo', 'vozes', 'modalização']


# --- prova ----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize('exame', EXAMES)
def test_prova_tem_a_pagina_de_cada_questao_do_gabarito(bronze, exame):
    pro = bronze[exame]['prova']
    assert Counter(chave(p) for p in pro) == Counter(chave(g) for g in bronze[exame]['gabarito'])
    paginas = [p['pagina'] for p in pro]
    assert paginas == sorted(paginas) and paginas[0] > 1  # na ordem do caderno, depois da capa


def test_prova_paginas_conferidas(bronze):
    def pagina(exame, questao, idioma=None):
        return next(p['pagina'] for p in bronze[exame]['prova'] if chave(p) == (questao, idioma))
    assert pagina('2027-1', 1) == 4
    assert pagina('2027-1', 5) == 5
    assert pagina('2024-1', 1) > 1  # a capa traz o número do exame no mesmo corpo da questão
