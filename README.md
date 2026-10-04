# Mapa das Questões UERJ

Site público e gratuito que mostra o que caiu nas provas objetivas do Vestibular Estadual da UERJ desde 2016, por ano,
exame, área, eixo, item e subitem do programa.

**Site: https://jnsadailton.github.io/mapeamento-questoes-uerj/**

Atualizado a cada push na `main` pelo GitHub Actions ([`.github/workflows/site.yml`](.github/workflows/site.yml)):
ingestão, testes, extração, `dbt build`, build do Evidence e publicação no GitHub Pages.

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
cd ../site                              # requer Node.js 20+
npm ci
npm run sources && npm run build        # site estático em site/build/
```

## Extração (camada bronze)

| Tabela | Uma linha por | Origem |
|---|---|---|
| `gabarito` | questão e idioma | gabarito oficial (resposta e data de aplicação) |
| `comentario` | comentário | gabarito comentado (percentual de acertos, nível, objetivo, texto) |
| `classificacao` | classificação de uma questão | gabarito comentado (eixo, item e subitem do programa) |
| `conteudo_programatico` | subitem do edital | anexo de conteúdos do edital (área, eixo, item, subitem) |
| `prova` | questão e idioma | caderno de prova (página em que a questão começa, para o site abrir o PDF nela) |

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
- **Língua estrangeira:** as versões em espanhol, francês e inglês são questões distintas em `fct_questao` e
  `fct_classificacao`, cada uma com gabarito, classificação e percentual de acertos próprios. Na **incidência**
  (`mart_incidencia`), a unidade é o número da questão no exame: se duas versões caem no mesmo conteúdo, ele conta uma
  vez (o candidato responde só um idioma, e contar as três daria peso triplo ao bloco); se caem em conteúdos diferentes,
  cada conteúdo conta. Nenhuma versão é descartada. Na **dificuldade** (`mart_dificuldade`), cada versão é um ponto,
  porque cada uma tem o próprio percentual. Uma questão com várias classificações conta para cada conteúdo.
- **Percentual de acertos:** existe para 1.248 das 1.482 versões de questão. A falta é uma limitação dos gabaritos
  comentados, não da extração. O gabarito comentado de 2021 existe, mas não tem o campo (nem o nível de dificuldade);
  o de 2024-2 traz o campo em branco; o de 2027-2 não o traz; e ele falta nas anuladas e em algumas questões de 2020-2
  e 2022-1.
- **Lacunas:** um subitem do edital vigente que nenhuma questão tocou desde 2016. As redações antigas de editais e
  comentários já chegam ligadas ao subitem atual equivalente, e o modelo mostra há quantos exames o subitem está no
  edital (alguns entraram só em 2024 ou 2027).

Testes do dbt: 60 questões por exame, anuladas exatamente as oficiais, toda questão não anulada classificada,
percentual entre 0 e 100 (e ausente onde o PDF não o publica), chaves únicas e estrangeiras, e nenhuma pendência.

## Site (Evidence)

Site estático feito com [Evidence](https://legacy-docs.evidence.dev/) (versão open source): páginas em Markdown + SQL,
com os filtros rodando no navegador (DuckDB-WASM). Criado por **Adailton Nascimento**.

| Página | O que mostra |
|---|---|
| Início | números gerais e destaques: o que mais cai, o que está em alta e o que sumiu mas costuma voltar |
| Programa | o dicionário completo do programa (área › eixo › item › subitem), com busca e as redações dos editais antigos |
| O que mais cai | filtros em cascata (vestibular, exame, área › disciplina › eixo › item, vários ao mesmo tempo); rankings de eixos, itens e subitens, concentração, links dos PDFs selecionados e a lista das questões da seleção |
| Tendências | regularidade, em alta e em baixa (2025–2027 contra os anos anteriores) e sumidos que costumam voltar, com filtros área › disciplina › eixo |
| Histórico por conteúdo | escolha guiada área › eixo › item; mapas de calor conteúdo × exame, do eixo ao subitem, e as questões do item |
| Dificuldade | filtros área › eixo › item; prioridade de estudo (questões × taxa de erro); frequência × acertos com a faixa de prioridade, que detalha de item para subitem, e a lista do que está nela; as questões mais difíceis |
| Lacunas | o que está no edital de 2027 e nunca caiu |
| Banco de questões | todas as questões, com filtros em cascata, classificação e links para a prova e o gabarito comentado, abertos na página da questão |

Os filtros de seleção múltipla são um componente próprio ([`site/components/Filtro.svelte`](site/components/Filtro.svelte)):
cada nível só oferece o que existe dentro do que está marcado acima (ex.: com só Linguagens, a disciplina oferece
Língua Portuguesa, Literatura e Língua Estrangeira).

Os indicadores de recorrência vêm do modelo `mart_recorrencia` e são descritivos: não preveem a próxima prova. A paleta
de cores (com a validação para daltonismo) está em [`docs/paleta-de-cores.md`](docs/paleta-de-cores.md). O logo da
UERJ é o arquivo oficial do kit de marca da universidade e identifica a fonte dos dados; o projeto é independente.

O Evidence 40 não tem tradução e compara o endereço das páginas sem o `basePath`. O script
[`site/scripts/traduzir-componentes.mjs`](site/scripts/traduzir-componentes.mjs), que roda sozinho depois do `npm ci`,
traduz os textos fixos dos componentes ("Select all", "Search"...) e corrige o menu lateral para marcar a página atual.

## Fontes

Os 84 PDFs usados (prova, gabarito, conteúdo programático e gabarito comentado de 21 exames) estão listados em
[`fontes/fontes.yml`](fontes/fontes.yml), cada um com o sha256 esperado. A ingestão tenta, nesta ordem, o site da UERJ,
uma captura do Wayback Machine e a cópia versionada em `fontes/pdfs/`, e usa a primeira que devolver o arquivo
idêntico. A fonte de cada arquivo fica registrada em `data/raw/proveniencia.csv`.

Sem internet, `uv run python -m uerj.ingestao --somente-repositorio` usa só a cópia versionada.

## Créditos

Criado por **Adailton Nascimento**. O desenvolvimento contou com o apoio do
[Claude Code](https://claude.com/claude-code), assistente de programação da Anthropic.
