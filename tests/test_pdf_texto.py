from uerj.extracao import pdf_texto


def test_sem_acento():
    assert pdf_texto.sem_acento('Questão de Química') == 'Questao de Quimica'
