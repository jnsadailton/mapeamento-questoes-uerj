"""Curadoria da hierarquia de conteúdo: normalização de textos e sugestões para o dicionário."""
import re
import unicodedata


def normalizar(texto):
    """Chave de comparação: minúsculas, sem acento e pontuação, palavras partidas na quebra de linha emendadas.

    Precisa dar o mesmo resultado que a macro `normalizar_texto` do dbt (dbt/macros/normalizar_texto.sql); o teste
    tests/test_curadoria.py confere as duas sobre todos os textos do dicionário.
    """
    s = ''.join(c for c in unicodedata.normalize('NFD', texto or '') if not unicodedata.combining(c)).lower()
    s = re.sub(r'(\w)- (\w)', r'\1\2', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
