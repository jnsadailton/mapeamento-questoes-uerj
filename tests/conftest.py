from concurrent.futures import ProcessPoolExecutor

import pytest

from uerj.extracao.bronze import extrair_exame
from uerj.ingestao.manifesto import EXAMES, RAIZ


@pytest.fixture(scope='session')
def bronze():
    """Saída dos parsers para os 21 exames, a partir da cópia versionada dos PDFs (fontes/pdfs/)."""
    with ProcessPoolExecutor() as ex:
        return dict(zip(EXAMES, ex.map(extrair_exame, EXAMES, [RAIZ / 'fontes' / 'pdfs'] * len(EXAMES))))
