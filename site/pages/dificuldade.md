---
title: Dificuldade
description: Onde os candidatos mais erram e o que cai muito e tem poucos acertos.
sidebar_position: 5
---

O gabarito comentado da UERJ publica o percentual de candidatos que acertaram cada questão. Aqui ele é cruzado com a
frequência de cada conteúdo, para mostrar onde vale mais a pena estudar: o que **cai muito e tem poucos acertos**.

<Alert status="info">
O percentual não existe para todas as questões, e a falta é da fonte oficial: o gabarito comentado de 2021 não tem o
campo, o de 2024-2 traz o campo em branco e o de 2027-2 não o publica. Faltam também as anuladas e algumas questões de
2020-2 e 2022-1. Essas questões ficam fora das médias.
</Alert>

```sql areas
select distinct area from uerj.conteudo order by area
```

<div class="filtros">

<Dropdown data={areas} name=areas value=area title="Área" multiple=true selectAllByDefault=true />

<Dropdown name=minimo title="Mínimo de questões por item" defaultValue=5>
  <DropdownOption value=3 valueLabel="3 ou mais" />
  <DropdownOption value=5 valueLabel="5 ou mais" />
  <DropdownOption value=10 valueLabel="10 ou mais" />
</Dropdown>

</div>

```sql itens
select
    d.rotulo as item,
    d.area,
    d.eixo,
    d.qtd_questoes as questoes_com_percentual,
    r.qtd_questoes as questoes,
    d.media_acertos / 100 as media,
    d.mediana_acertos / 100 as mediana,
    d.min_acertos / 100 as minimo,
    d.max_acertos / 100 as maximo,
    r.qtd_questoes * (1 - d.media_acertos / 100) as erros_esperados
from uerj.dificuldade as d
inner join uerj.recorrencia as r on r.nivel = 'item' and r.id_conteudo = d.id_conteudo
where d.nivel = 'item' and d.area in ${inputs.areas.value} and d.qtd_questoes >= ${inputs.minimo.value}
```

## Prioridade de estudo

O índice de prioridade multiplica as questões do item desde 2016 pela taxa de erro média: é quantas dessas questões
um candidato típico errou. Quanto maior, mais o item pesa e mais derruba.

```sql prioridade
select
    case when length(item) > 48 then left(item, 47) || '…' else item end as rotulo,
    item,
    area,
    questoes,
    media,
    erros_esperados
from ${itens}
order by erros_esperados desc
limit 15
```

<BarChart
  data={prioridade}
  x=rotulo
  y=erros_esperados
  series=area
  seriesOrder={['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas']}
  seriesColors={{'Linguagens': 'area-lin', 'Matemática': 'area-mat', 'Ciências da Natureza': 'area-cnt', 'Ciências Humanas': 'area-chs'}}
  swapXY=true
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  labelFmt="0"
  yFmt="0"
  xAxisTitle=" "
  yAxisTitle="Questões erradas por um candidato típico"
  chartAreaHeight=440
  emptySet=pass
  emptyMessage="Nenhum item com percentual publicado nesta seleção."
/>

## Frequência × acertos

Cada ponto é um item. À direita, os que mais caem; embaixo, os que têm menos acertos. O canto **inferior direito** é o
mais importante: cai muito e quase ninguém acerta. As linhas marcam a média da área.

```sql uma_area
select distinct area from uerj.conteudo order by area
```

<Dropdown data={uma_area} name=area_dispersao value=area title="Área do gráfico" defaultValue="Matemática" />

```sql dispersao
select item, eixo, questoes, media from ${itens} where area = '${inputs.area_dispersao.value}'
```

```sql medias
select avg(questoes) as questoes, avg(media) as media from ${dispersao}
```

<ScatterPlot
  data={dispersao}
  x=questoes
  y=media
  tooltipTitle=item
  yFmt=pct0
  yMin=0
  yMax=1
  pointSize=12
  xAxisTitle="Questões desde 2016"
  yAxisTitle="Média de acertos"
  emptySet=pass
  emptyMessage="Nenhum item com percentual publicado nesta área."
>
  {#if medias.length && medias[0].media != null}
    <ReferenceLine y={medias[0].media} label="média de acertos" hideValue=true lineType=dashed />
    <ReferenceLine x={medias[0].questoes} label="média de questões" hideValue=true lineType=dashed />
  {/if}
</ScatterPlot>

O gráfico mostra uma área por vez para os pontos não se confundirem. Passe o mouse sobre um ponto para ver o item.

## Todos os itens

<DataTable data={itens} rows=10 search=true sort="media" emptySet=pass emptyMessage="Nenhum item nesta seleção.">
  <Column id=item title="Item" wrap=true />
  <Column id=area title="Área" />
  <Column id=questoes title="Questões" />
  <Column id=media title="Média de acertos" fmt=pct0 contentType=bar barColor="#9cc8f0" />
  <Column id=mediana title="Mediana" fmt=pct0 />
  <Column id=minimo title="Mínimo" fmt=pct0 />
  <Column id=maximo title="Máximo" fmt=pct0 />
</DataTable>

Cada versão de questão com percentual publicado é um ponto da média; no bloco de língua estrangeira, cada idioma conta
separadamente. Itens com poucas questões têm médias instáveis, por isso o filtro de mínimo.

## As questões mais difíceis

```sql questoes_dificeis
select id_questao, area, classificacao, percentual_acertos / 100 as acertos, url_comentario
from uerj.questoes
where percentual_acertos is not null and area in ${inputs.areas.value}
order by percentual_acertos
limit 25
```

<DataTable data={questoes_dificeis} rows=10 emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=area title="Área" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=url_comentario title="Comentário" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

## Média de acertos por exame

```sql por_exame
select rotulo_curto, id_exame, media_acertos / 100 as media
from uerj.exames
where media_acertos is not null
order by id_exame
```

<LineChart
  data={por_exame}
  x=rotulo_curto
  y=media
  sort=false
  markers=true
  markerSize=8
  lineWidth=2
  labels=true
  labelFmt=pct0
  yFmt=pct0
  yMin=0
  yMax=1
  xAxisTitle="Exame"
  yAxisTitle="Média de acertos"
  emptySet=pass
/>

Faltam 2021, 2024-2 e 2027-2, que não têm percentual publicado. A média de acertos fica entre 47% e 61% em todos os
exames.

<style>
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.75rem; align-items: flex-end; margin: 0.5rem 0 1rem; }
</style>
