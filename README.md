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
uv run python -m uerj.extracao          # extrai os PDFs para data/bronze/ (Parquet)
cd dbt
uv run dbt build --profiles-dir .       # modelos e testes em data/warehouse/uerj.duckdb
uv run dbt docs generate --profiles-dir . && uv run dbt docs serve --profiles-dir .
```

## Extração (camada bronze)

| Tabela | Uma linha por | Origem |
|---|---|---|
| `gabarito` | questão e idioma | gabarito oficial (resposta e data de aplicação) |
| `comentario` | comentário | gabarito comentado (percentual de acertos, nível, objetivo, texto) |
| `classificacao` | classificação de uma questão | gabarito comentado (eixo, item e subitem do programa) |
| `conteudo_programatico` | subitem do edital | anexo de conteúdos do edital (área, eixo, item, subitem) |

Os PDFs mudam de layout ao longo dos anos. Os gabaritos são lidos pela posição das palavras na página, e nos
gabaritos comentados cada comentário é ligado ao rótulo da questão pela posição, porque a ordem do texto extraído é
embaralhada. Os testes em `tests/test_extracao.py` cobrem os 21 exames e as lacunas conhecidas das próprias fontes.

## Modelagem (dbt + DuckDB)

```text
bronze (Parquet) ─► staging ─► intermediate ─────────────────► marts
seeds de curadoria ───────────┘  curadoria, partes do subitem,   dim_exame, dim_conteudo, fct_questao,
                                 ligação pelo dicionário          fct_classificacao, bridge_programa_ano,
                                                                  mart_incidencia, mart_dificuldade, mart_lacunas
```

O texto de eixo, item e subitem muda de um edital para outro e os comentários o reescrevem de muitas formas
("sequências" e "sucessões", "lei de Stevin" e "lei se Stevin", subitens antigos que viraram outro item). Para comparar
os anos, todo texto passa por uma **hierarquia canônica** (Área › Eixo › Item › Subitem, IDs como `MAT.2.03.01`):

| Seed | Papel |
|---|---|
| `conteudo_base.csv` | a hierarquia: base no edital de 2027, com os conteúdos de editais antigos marcados como fora do edital vigente |
| `dicionario_conteudo.csv` | cada texto (item, subitem) visto num edital ou comentário → um ou mais conteúdos canônicos, com o método (exato, similar, manual) e a justificativa das decisões manuais |
| `correcoes.csv` | classificações transcritas da imagem do PDF, feitas à mão (questão sem comentário) ou completadas quando o PDF omite ou troca eixo, item ou subitem |
| `eixos_atribuidos.csv` | eixo tirado do edital quando o comentário não o informa |

O que o projeto completou ou estimou leva um adendo público (`observacao`), exibido junto da questão. Um texto que não
casa com o dicionário vai para o modelo `pendencias` e faz o teste `assert_sem_pendencias` falhar;
`uv run python -m uerj.curadoria` sugere as ligações para revisão.

Decisões de modelagem:

- **Disciplina:** Ciências da Natureza separada em Física, Química e Biologia (pelo item), Linguagens em Língua
  Portuguesa, Literatura e Língua Estrangeira. Ciências Humanas fica como área única, porque os editais tratam
  Geografia e História de forma integrada (quase todo item aparece nas duas).
- **Contagem:** nos marts, a unidade é o número da questão no exame. As três versões de língua estrangeira ocupam o
  mesmo número e contam uma vez; uma questão com várias classificações conta para cada conteúdo.

Testes do dbt: 60 questões por exame, anuladas exatamente as oficiais, toda questão não anulada classificada,
percentual entre 0 e 100 (e ausente onde o PDF não o publica), chaves únicas e estrangeiras, e nenhuma pendência.

## Fontes

Os 84 PDFs usados (prova, gabarito, conteúdo programático e gabarito comentado de 21 exames) estão listados em
[`fontes/fontes.yml`](fontes/fontes.yml), cada um com o sha256 esperado. A ingestão tenta, nesta ordem, o site da UERJ,
uma captura do Wayback Machine e a cópia versionada em `fontes/pdfs/`, e usa a primeira que devolver o arquivo
idêntico. A fonte de cada arquivo fica registrada em `data/raw/proveniencia.csv`.

Sem internet, `uv run python -m uerj.ingestao --somente-repositorio` usa só a cópia versionada.
