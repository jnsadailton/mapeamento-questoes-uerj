# Mapa das Questões UERJ

Site público e gratuito que mostra o que caiu nas provas objetivas do Vestibular Estadual da UERJ desde 2016, por ano,
exame, área, eixo, item e subitem do programa.

> Projeto em construção. Esta página será completada quando o site estiver no ar.

## Pipeline

```text
PDFs oficiais ──► Ingestão ──► Extração ──► Transformação ──► Site estático interativo
                   (raw)        (bronze)     (dbt + DuckDB)     (Evidence.dev)
        └──────────────── orquestrado pelo GitHub Actions ────────────────┘
```

## Como rodar

Requer Python 3.12 e [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run python -m uerj.ingestao          # baixa os PDFs para data/raw/
```

## Fontes

Os 84 PDFs usados (prova, gabarito, conteúdo programático e gabarito comentado de 21 exames) estão listados em
[`fontes/fontes.yml`](fontes/fontes.yml), cada um com o sha256 esperado. A ingestão tenta, nesta ordem, o site da UERJ,
uma captura do Wayback Machine e a cópia versionada em `fontes/pdfs/`, e usa a primeira que devolver o arquivo
idêntico. A fonte de cada arquivo fica registrada em `data/raw/proveniencia.csv`.

Sem internet, `uv run python -m uerj.ingestao --somente-repositorio` usa só a cópia versionada.
