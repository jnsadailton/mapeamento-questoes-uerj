import csv
import hashlib
import ssl
from urllib.error import URLError

import pytest

from uerj.ingestao import catalogo
from uerj.ingestao.obter import obter, obter_todos

CONTEUDO = b'%PDF-1.4 conteudo do teste'
OUTRO = b'%PDF-1.4 versao retificada'


@pytest.fixture
def raiz(tmp_path):
    copia = tmp_path / 'fontes' / 'pdfs' / '2016-1' / '2016-1_prova.pdf'
    copia.parent.mkdir(parents=True)
    copia.write_bytes(CONTEUDO)
    return tmp_path


@pytest.fixture
def doc():
    return catalogo.Documento(
        exame='2016-1', tipo='prova', arquivo='fontes/pdfs/2016-1/2016-1_prova.pdf',
        sha256=hashlib.sha256(CONTEUDO).hexdigest(), tamanho=len(CONTEUDO),
        url_oficial='https://uerj.exemplo/prova.pdf',
        url_wayback='https://web.archive.org/web/20200101000000id_/https://uerj.exemplo/prova.pdf',
        coletado_em='2026-10-02')


def baixador(respostas):
    """Simula a rede: cada URL devolve bytes ou levanta a exceção cadastrada."""
    chamadas = []

    def baixar(url):
        chamadas.append(url)
        r = respostas[url]
        if isinstance(r, Exception):
            raise r
        return r
    baixar.chamadas = chamadas
    return baixar


def test_usa_uerj_quando_responde(doc, raiz, tmp_path):
    b = baixador({doc.url_oficial: CONTEUDO})
    p = obter(doc, tmp_path / 'raw', baixar=b, raiz=raiz)
    assert p.fonte == 'uerj' and p.avisos == ''
    assert b.chamadas == [doc.url_oficial]
    assert (tmp_path / 'raw' / '2016-1' / '2016-1_prova.pdf').read_bytes() == CONTEUDO


def test_cai_para_wayback_quando_uerj_fora_do_ar(doc, raiz, tmp_path):
    b = baixador({doc.url_oficial: TimeoutError('sem resposta'), doc.url_wayback: CONTEUDO})
    p = obter(doc, tmp_path / 'raw', baixar=b, raiz=raiz)
    assert p.fonte == 'wayback' and p.url == doc.url_wayback
    assert 'uerj: falhou' in p.avisos


def test_certificado_vencido_da_uerj_vale_se_o_sha256_confere(doc, raiz, tmp_path):
    vencido = ssl.SSLCertVerificationError('certificate has expired')
    vencido.verify_code = 10
    chamadas = []

    def baixar(url, verificar=True):
        chamadas.append((url, verificar))
        if verificar:
            raise URLError(vencido)
        return CONTEUDO
    p = obter(doc, tmp_path / 'raw', baixar=baixar, raiz=raiz)
    assert p.fonte == 'uerj' and 'certificado SSL do servidor vencido' in p.avisos
    assert chamadas == [(doc.url_oficial, True), (doc.url_oficial, False)]


def test_outro_erro_de_certificado_nao_e_ignorado(doc, raiz, tmp_path):
    invalido = ssl.SSLCertVerificationError('self-signed certificate')
    invalido.verify_code = 18
    b = baixador({doc.url_oficial: URLError(invalido), doc.url_wayback: CONTEUDO})
    p = obter(doc, tmp_path / 'raw', baixar=b, raiz=raiz)
    assert p.fonte == 'wayback'


def test_hash_diferente_nao_substitui_em_silencio(doc, raiz, tmp_path):
    b = baixador({doc.url_oficial: OUTRO, doc.url_wayback: ConnectionError('fora')})
    p = obter(doc, tmp_path / 'raw', baixar=b, raiz=raiz)
    assert p.fonte == 'repositorio'
    assert 'uerj: sha256 diferente' in p.avisos
    assert (tmp_path / 'raw' / '2016-1' / '2016-1_prova.pdf').read_bytes() == CONTEUDO


def test_somente_repositorio_nao_acessa_a_rede(doc, raiz, tmp_path):
    b = baixador({})
    p = obter(doc, tmp_path / 'raw', fontes=('repositorio',), baixar=b, raiz=raiz)
    assert p.fonte == 'repositorio' and b.chamadas == []


def test_falha_quando_nenhuma_fonte_confere(doc, raiz, tmp_path):
    (raiz / doc.arquivo).write_bytes(OUTRO)
    b = baixador({doc.url_oficial: OUTRO, doc.url_wayback: OUTRO})
    with pytest.raises(RuntimeError, match='nenhuma fonte'):
        obter(doc, tmp_path / 'raw', baixar=b, raiz=raiz)


def test_grava_proveniencia(doc, raiz, tmp_path):
    obter_todos([doc], tmp_path / 'raw', fontes=('repositorio',), raiz=raiz)
    linhas = list(csv.DictReader(open(tmp_path / 'raw' / 'proveniencia.csv', encoding='utf-8')))
    assert len(linhas) == 1 and linhas[0]['fonte'] == 'repositorio'


def test_catalogo_completo():
    docs = catalogo.carregar()
    assert len(docs) == 84
    assert len({d.exame for d in docs}) == 21


def test_catalogo_confere_com_copias_versionadas():
    for d in catalogo.carregar():
        b = (catalogo.RAIZ / d.arquivo).read_bytes()
        assert len(b) == d.tamanho, d.nome
        assert hashlib.sha256(b).hexdigest() == d.sha256, d.nome


def test_catalogo_rejeita_documento_faltando():
    docs = catalogo.carregar()[1:]
    with pytest.raises(ValueError, match='faltam documentos'):
        catalogo.validar(docs)
