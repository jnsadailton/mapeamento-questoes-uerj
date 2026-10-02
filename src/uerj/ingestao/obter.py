"""Obtém cada PDF do manifesto e grava em data/raw/, registrando de qual fonte veio.

Ordem das fontes: site da UERJ, Wayback Machine e, por último, a cópia versionada em fontes/pdfs/. Vale a primeira que
devolver o arquivo com o sha256 esperado. Um arquivo com hash diferente nunca é usado: vira aviso na proveniência.
"""
import csv
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from .manifesto import RAIZ

log = logging.getLogger(__name__)

DESTINO = RAIZ / 'data' / 'raw'
CABECALHO = {'User-Agent': 'mapeamento-questoes-uerj (+https://github.com/jnsadailton/mapeamento-questoes-uerj)'}


@dataclass
class Proveniencia:
    exame: str
    tipo: str
    arquivo: str
    sha256: str
    fonte: str  # uerj, wayback ou repositorio
    url: str
    obtido_em: str
    avisos: str


def baixar(url, timeout=60, tentativas=2):
    """Baixa a URL e devolve os bytes. Levanta a última exceção se todas as tentativas falharem."""
    for i in range(tentativas):
        try:
            with urlopen(Request(url, headers=CABECALHO), timeout=timeout) as r:
                return r.read()
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(2 * (i + 1))


FONTES = ('uerj', 'wayback', 'repositorio')


def obter(doc, destino=DESTINO, fontes=FONTES, baixar=baixar, raiz=RAIZ):
    """Grava o PDF do documento em destino/<exame>/ e devolve a proveniência."""
    avisos = []
    urls = {'uerj': doc.url_oficial, 'wayback': doc.url_wayback, 'repositorio': None}
    for fonte in FONTES:
        url = urls[fonte]
        if fonte not in fontes or (fonte == 'wayback' and not url):
            continue
        try:
            conteudo = (raiz / doc.arquivo).read_bytes() if fonte == 'repositorio' else baixar(url)
        except Exception as e:
            avisos.append(f'{fonte}: falhou ({type(e).__name__}: {e})')
            continue
        sha = hashlib.sha256(conteudo).hexdigest()
        if sha != doc.sha256:
            avisos.append(f'{fonte}: sha256 diferente do manifesto ({sha})')
            log.warning('%s: %s devolveu sha256 diferente do manifesto; arquivo ignorado', doc.nome, fonte)
            continue
        alvo = Path(destino) / doc.exame / doc.nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(conteudo)
        return Proveniencia(doc.exame, doc.tipo, f'{doc.exame}/{doc.nome}', sha, fonte,
                            url or doc.arquivo, datetime.now(timezone.utc).isoformat(timespec='seconds'),
                            ' | '.join(avisos))
    raise RuntimeError(f'{doc.nome}: nenhuma fonte devolveu o arquivo esperado\n' + '\n'.join(avisos))


def obter_todos(docs, destino=DESTINO, paralelo=4, **kw):
    """Obtém todos os documentos e grava destino/proveniencia.csv e destino/fontes.csv (o manifesto em CSV)."""
    with ThreadPoolExecutor(paralelo) as ex:
        provs = list(ex.map(lambda d: obter(d, destino, **kw), docs))
    Path(destino).mkdir(parents=True, exist_ok=True)
    for nome, linhas in (('proveniencia.csv', [asdict(p) for p in provs]), ('fontes.csv', [asdict(d) for d in docs])):
        with open(Path(destino) / nome, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0]))
            w.writeheader()
            w.writerows(linhas)
    return provs
