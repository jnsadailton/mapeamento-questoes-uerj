"""Testes dos parsers sobre a cópia versionada dos PDFs (fontes/pdfs/), com os casos especiais conhecidos."""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import pytest

from uerj.extracao.bronze import extrair_exame
from uerj.ingestao.manifesto import EXAMES, RAIZ

PDFS = RAIZ / 'fontes' / 'pdfs'
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


@pytest.fixture(scope='module')
def bronze():
    with ProcessPoolExecutor() as ex:
        return dict(zip(EXAMES, ex.map(extrair_exame, EXAMES, [PDFS] * len(EXAMES))))


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
        # só faltam os das anuladas e poucos casos em que o PDF não traz o campo (2020-2 e 2022-1)
        assert len(percentuais) >= len(com) - (12 if exame == '2022-1' else 2)


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
    # texto da questão seguinte não vaza para o fim do comentário
    assert comentario('2024-1', 11)['texto'].endswith('Nível de dificuldade: fácil.')
    assert comentario('2024-1', 11)['nivel'] == 'facil'


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


def test_conteudo_subitens_separados_por_ponto_e_virgula(bronze):
    subitens = [c['subitem'] for c in bronze['2016-1']['conteudo_programatico']
                if c['item'] == 'Perspectivas enunciativas']
    assert subitens == ['quem enuncia, a quem enuncia, espaço, tempo', 'vozes', 'modalização']
