---
title: O que mais cai
description: Escolha vestibulares, exames e disciplinas e veja os eixos, itens e subitens que mais caíram.
sidebar_position: 2
---

<script>
  // Cor fixa por área (tokens do tema, ver docs/paleta-de-cores.md)
  const coresArea = {
    'Linguagens': 'area-lin',
    'Matemática': 'area-mat',
    'Ciências da Natureza': 'area-cnt',
    'Ciências Humanas': 'area-chs'
  };
  const ordemAreas = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];
  const corTreemap = { 'Linguagens': '#0072CE', 'Matemática': '#eb6834', 'Ciências da Natureza': '#1baf7a', 'Ciências Humanas': '#eda100' };
  const textoTreemap = { 'Linguagens': '#ffffff', 'Matemática': '#ffffff', 'Ciências da Natureza': '#0b0b0b', 'Ciências Humanas': '#0b0b0b' };

  function arvore(linhas) {
    const areas = new Map();
    for (const l of linhas) {
      if (!areas.has(l.area)) areas.set(l.area, new Map());
      const eixos = areas.get(l.area);
      if (!eixos.has(l.eixo)) eixos.set(l.eixo, []);
      eixos.get(l.eixo).push({ name: l.item, value: l.questoes, label: { color: textoTreemap[l.area] } });
    }
    return [...areas].map(([area, eixos]) => ({
      name: area,
      itemStyle: { color: corTreemap[area] },
      upperLabel: { color: textoTreemap[area] },
      children: [...eixos].map(([eixo, itens]) => ({ name: eixo, upperLabel: { color: textoTreemap[area] }, children: itens }))
    }));
  }

  $: linhasTreemap = arvore_sel && arvore_sel.length ? Array.from(arvore_sel) : [];
  $: configTreemap = {
    tooltip: {
      formatter: (p) => `${p.treePathInfo.slice(1).map((n) => n.name).join(' › ')}<br/><b>${p.value}</b> questão(ões)`
    },
    series: [{
      type: 'treemap',
      data: arvore(linhasTreemap),
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      width: '100%',
      height: '100%',
      top: 0,
      label: { show: true, formatter: '{b}', overflow: 'truncate', ellipsis: '…', fontSize: 11 },
      upperLabel: { show: true, height: 18, fontSize: 11, overflow: 'truncate', ellipsis: '…' },
      levels: [
        { itemStyle: { borderColor: 'transparent', borderWidth: 0, gapWidth: 3 }, upperLabel: { show: false } },
        { itemStyle: { borderColor: 'rgba(0,0,0,0.12)', borderWidth: 2, gapWidth: 2 }, colorSaturation: [0.35, 0.6] },
        { itemStyle: { gapWidth: 1, borderColorSaturation: 0.6 }, colorSaturation: [0.35, 0.55] }
      ]
    }]
  };

  $: nomeNivel = { eixo: 'eixos', item: 'itens', subitem: 'subitens' }[inputs.nivel] ?? 'itens';
</script>

Monte a sua seleção: um ou mais vestibulares, os exames e as disciplinas que interessam. Tudo abaixo se atualiza na
hora: o ranking, o mapa da prova, os indicadores e os links das provas escolhidas.

```sql anos
select distinct ano, rotulo_ano from uerj.exames order by ano desc
```

```sql etapas
select etapa, min(numero) as ordem from uerj.exames group by etapa
```

```sql disciplinas
select distinct disciplina from uerj.classificacoes order by disciplina
```

<div class="filtros">

<Dropdown data={anos} name=anos value=ano label=rotulo_ano title="Vestibular" multiple=true selectAllByDefault=true order="ano desc" />

<Dropdown data={etapas} name=etapas value=etapa title="Exame" multiple=true selectAllByDefault=true order="ordem" />

<Dropdown data={disciplinas} name=disciplinas value=disciplina title="Disciplina" multiple=true selectAllByDefault=true />

<ButtonGroup name=nivel title="Ver por" color="#0072CE">
  <ButtonGroupItem valueLabel="Eixo" value="eixo" />
  <ButtonGroupItem valueLabel="Item" value="item" default />
  <ButtonGroupItem valueLabel="Subitem" value="subitem" />
</ButtonGroup>

</div>

```sql sel_exames
select *
from uerj.exames
where ano in ${inputs.anos.value} and etapa in ${inputs.etapas.value}
order by id_exame desc
```

```sql sel_class
select *
from uerj.classificacoes
where id_exame in (select id_exame from ${sel_exames}) and disciplina in ${inputs.disciplinas.value}
```

```sql kpis
select
    (select count(*) from ${sel_exames}) as exames,
    count(distinct id_exame || '-' || numero) as questoes,
    count(distinct id_item) as itens,
    count(distinct id_subitem) as subitens,
    (select avg(p) / 100 from (select distinct id_questao, percentual_acertos as p from ${sel_class})) as media_acertos
from ${sel_class}
```

<Grid cols=4>
  <BigValue data={kpis} value=exames title="Exames selecionados" emptySet=pass emptyMessage="—" />
  <BigValue data={kpis} value=questoes fmt="0" title="Questões na seleção" emptySet=pass emptyMessage="—" />
  <BigValue data={kpis} value=itens title="Itens diferentes cobrados" emptySet=pass emptyMessage="—" />
  <BigValue data={kpis} value=media_acertos fmt=pct0 title="Média de acertos" emptySet=pass emptyMessage="não publicada" />
</Grid>

{#if kpis.length && kpis[0].questoes === 0}

<Alert status="warning">Nenhuma questão nesta seleção. Escolha pelo menos um vestibular, um exame e uma disciplina.</Alert>

{/if}

## Ranking: o que mais caiu

```sql ranking
select
    case '${inputs.nivel}' when 'eixo' then eixo when 'item' then item else subitem end as conteudo,
    case '${inputs.nivel}' when 'eixo' then area when 'item' then eixo else item end as dentro_de,
    area,
    count(distinct id_exame || '-' || numero) as questoes,
    count(distinct id_exame) as exames
from ${sel_class}
where '${inputs.nivel}' <> 'subitem' or id_subitem is not null
group by all
```

```sql ranking_total
select
    r.*,
    r.questoes / sum(r.questoes) over () as participacao,
    r.exames / (select count(*) from ${sel_exames}) as frequencia
from ${ranking} as r
order by questoes desc, exames desc, conteudo
```

```sql top15
select
    case when length(conteudo) > 48 then left(conteudo, 47) || '…' else conteudo end as rotulo,
    area,
    questoes
from ${ranking_total}
limit 15
```

<BarChart
  data={top15}
  x=rotulo
  y=questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  swapXY=true
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  chartAreaHeight=440
  emptySet=pass
  emptyMessage="Nenhum conteúdo para esta seleção."
/>

<DataTable data={ranking_total} rows=10 search=true emptySet=pass emptyMessage="Nenhum conteúdo para esta seleção.">
  <Column id=conteudo title="Conteúdo" wrap=true />
  <Column id=dentro_de title="Dentro de" wrap=true />
  <Column id=questoes title="Questões" contentType=bar barColor="#9cc8f0" />
  <Column id=participacao title="% das questões" fmt=pct0 />
  <Column id=exames title="Exames em que caiu" />
  <Column id=frequencia title="% dos exames" fmt=pct0 />
</DataTable>

**Como ler:** *questões* conta cada número de questão uma vez (as versões de espanhol, francês e inglês do mesmo número
contam juntas). *% dos exames* mostra a regularidade: 100% quer dizer que caiu em todos os exames selecionados.

```sql concentracao
with r as (
    select
        questoes,
        sum(questoes) over (order by questoes desc, conteudo rows unbounded preceding) as acumulado,
        sum(questoes) over () as total
    from ${ranking}
)
select
    count(*) filter (where acumulado - questoes < total * 0.5) as para_metade,
    count(*) as distintos
from r
having count(*) > 0
```

{#if concentracao.length && concentracao[0].distintos > 0}

<Alert status="info">
<b>Concentração:</b> {concentracao[0].para_metade} dos {concentracao[0].distintos} {nomeNivel} cobrados nesta seleção
respondem por metade das questões. Comece por eles.
</Alert>

{/if}

## O mapa da seleção

Cada retângulo é um item do programa, agrupado por eixo e área; o tamanho é o número de questões. Passe o mouse para
ver o caminho completo.

```sql arvore_sel
select area, eixo, item, count(distinct id_exame || '-' || numero) as questoes
from ${sel_class}
group by all
order by area, eixo, questoes desc
```

{#if linhasTreemap.length}

<ECharts config={configTreemap} height="500px" />

{:else}

<Alert status="warning">Nada para mostrar: a seleção não tem questões.</Alert>

{/if}

## Quanto cada disciplina pesou

```sql por_disciplina
select
    disciplina,
    area,
    count(distinct id_exame || '-' || numero) as questoes
from ${sel_class}
group by all
order by questoes desc
```

<BarChart
  data={por_disciplina}
  x=disciplina
  y=questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  swapXY=true
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  emptySet=pass
  emptyMessage="Nenhuma disciplina para esta seleção."
/>

Uma questão interdisciplinar conta para cada disciplina em que foi classificada. Ciências Humanas aparece inteira
porque os editais não separam Geografia e História.

## As provas selecionadas

Links para os PDFs oficiais de cada exame da seleção.

<DataTable data={sel_exames} rows=12 emptySet=pass emptyMessage="Nenhum exame selecionado.">
  <Column id=nome title="Exame" />
  <Column id=data_aplicacao title="Aplicação" fmt="dd/mm/yyyy" />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_gabarito title="Gabarito" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_gabarito_comentado title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_conteudo_programatico title="Conteúdo programático" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

## Curiosidade: a letra do gabarito

```sql letras
select resposta as letra, count(*) as questoes
from uerj.questoes
where id_exame in (select id_exame from ${sel_exames}) and not anulada
group by all
order by letra
```

<BarChart
  data={letras}
  x=letra
  y=questoes
  sort=false
  labels=true
  xAxisTitle="Alternativa correta"
  yAxisTitle="Questões"
  emptySet=pass
  emptyMessage="Nenhuma questão para esta seleção."
/>

A UERJ distribui as respostas entre as quatro alternativas de forma equilibrada: a letra do gabarito não ajuda a
acertar uma questão.

<style>
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.75rem; align-items: flex-end; margin: 0.5rem 0 1rem; }
  .filtros :global(p) { margin: 0; }
</style>
