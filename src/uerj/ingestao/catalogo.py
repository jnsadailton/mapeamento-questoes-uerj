"""Leitura e validação do catálogo dos PDFs (fontes/fontes.yml)."""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[3]
CATALOGO = RAIZ / 'fontes' / 'fontes.yml'

TIPOS = ('prova', 'gabarito', 'conteudo_programatico', 'gabarito_comentado')
EXAMES = tuple(f'{a}-{n}' for a in range(2016, 2028) for n in ((1,) if a in (2021, 2022, 2023) else (1, 2)))


@dataclass(frozen=True)
class Documento:
    exame: str
    tipo: str
    arquivo: str
    sha256: str
    tamanho: int
    url_oficial: str
    url_wayback: str | None
    coletado_em: str

    @property
    def nome(self):
        return f'{self.exame}_{self.tipo}.pdf'


def carregar(caminho=CATALOGO):
    """Lê o catálogo e devolve a lista de documentos, já validada."""
    dados = yaml.safe_load(Path(caminho).read_text(encoding='utf-8'))
    docs = [Documento(**{**d, 'coletado_em': str(d['coletado_em'])}) for d in dados['documentos']]
    validar(docs)
    return docs


def validar(docs):
    erros = []
    chaves = [(d.exame, d.tipo) for d in docs]
    if len(set(chaves)) != len(chaves):
        erros.append('há documentos repetidos')
    faltando = {(e, t) for e in EXAMES for t in TIPOS} - set(chaves)
    if faltando:
        erros.append(f'faltam documentos: {sorted(faltando)}')
    for d in docs:
        if d.exame not in EXAMES or d.tipo not in TIPOS:
            erros.append(f'{d.exame} {d.tipo}: exame ou tipo fora do escopo')
        if not re.fullmatch(r'[0-9a-f]{64}', d.sha256):
            erros.append(f'{d.nome}: sha256 inválido')
        if d.arquivo != f'fontes/pdfs/{d.exame}/{d.nome}':
            erros.append(f'{d.nome}: caminho da cópia fora do padrão ({d.arquivo})')
        if not d.url_oficial.startswith('https://'):
            erros.append(f'{d.nome}: url_oficial deve usar https')
        if d.url_wayback and not re.match(r'https://web\.archive\.org/web/\d{14}id_/', d.url_wayback):
            erros.append(f'{d.nome}: url_wayback deve apontar para o arquivo original (<timestamp>id_)')
    if erros:
        raise ValueError('catálogo inválido:\n' + '\n'.join(erros))
