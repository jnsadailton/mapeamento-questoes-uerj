from pathlib import Path

from uerj.extracao import pdf_texto

PDFS = Path(__file__).resolve().parents[1] / 'fontes' / 'pdfs'


def test_sem_acento():
    assert pdf_texto.sem_acento('Questão de Química') == 'Questao de Quimica'


def test_pdfs_versionados_presentes():
    pdfs = sorted(PDFS.glob('*/*.pdf'))
    assert len(pdfs) == 84
