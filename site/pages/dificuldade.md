---
title: Dificuldade
description: Onde os candidatos mais erram e o que cai muito e tem poucos acertos.
sidebar_position: 6
---

<script>
  import { AREAS, criarCascata, gravarInputs, linhasDe, naOrdem, paraInput } from '$lib/filtros.js';

  // Área › Eixo › Item: valem para a página inteira.
  const conteudo = criarCascata([
    { nome: 'areas', valor: 'area', ordenar: naOrdem(AREAS) },
    { nome: 'eixos', valor: 'id_eixo', rotulo: 'eixo' },
    { nome: 'itens', valor: 'id_item', rotulo: 'item' }
  ]);
  $: hier = linhasDe(hierarquia);
  let sel = null;
  $: if (!sel && hier.length) sel = conteudo.inicial(hier);
  $: opc = sel ? conteudo.opcoes(hier, sel) : {};
  const escolher = (nome, valores) => (sel = conteudo.escolher(hier, sel, nome, valores));
  const limparFiltros = () => (sel = conteudo.inicial(hier));
  $: if (sel)
    gravarInputs(inputs_store, {
      areas: paraInput(sel.areas, opc.areas),
      eixos: paraInput(sel.eixos, opc.eixos),
      itens: paraInput(sel.itens, opc.itens)
    });

  // Cada eixo tem cor e formato fixos dentro da área (na ordem do programa): a cor sozinha não distingue quatro eixos
  // quando os pontos se sobrepõem (docs/paleta-de-cores.md).
  const FORMAS = ['circle', 'rect', 'triangle', 'diamond'];
  $: estiloEixo = (() => {
    const porArea = new Map();
    for (const r of hier) {
      if (!porArea.has(r.area)) porArea.set(r.area, new Map());
      porArea.get(r.area).set(r.id_eixo, r.eixo);
    }
    const estilo = {};
    for (const eixos of porArea.values())
      [...eixos].sort(([a], [b]) => a.localeCompare(b)).forEach(([id, nome], i) => {
        estilo[nome] = { id, cor: 'eixo-' + ((i % 4) + 1), forma: FORMAS[i % 4] };
      });
    return estilo;
  })();
  $: coresEixos = Object.fromEntries(Object.entries(estiloEixo).map(([nome, e]) => [nome, e.cor]));

  // Detalhamento: com todos os itens marcados, cada ponto é um item (um gráfico por área); com só alguns itens
  // marcados, cada ponto é um subitem (um gráfico por item).
  $: porSubitem = !!sel && (opc.itens ?? []).length > 0 && sel.itens.length < opc.itens.length;
  $: nivelPontos = porSubitem ? 'subitem' : 'item';
  $: pontos = linhasDe(dispersao).filter((r) => r.nivel === nivelPontos);
  const media = (l, campo) => l.reduce((t, r) => t + Number(r[campo]), 0) / l.length;
  const porId = (a, b) => (estiloEixo[a]?.id ?? '').localeCompare(estiloEixo[b]?.id ?? '');
  $: grupos = (() => {
    const mapa = new Map();
    for (const r of pontos) {
      const chave = porSubitem ? r.id_item : r.area;
      if (!mapa.has(chave))
        mapa.set(chave, { chave, titulo: porSubitem ? r.item : r.area, sub: porSubitem ? 'eixo ' + r.eixo : '', pontos: [] });
      mapa.get(chave).pontos.push(r);
    }
    const lista = [...mapa.values()].map((g) => ({
      ...g,
      eixos: [...new Set(g.pontos.map((p) => p.eixo))].sort(porId),
      mediaQ: media(g.pontos, 'questoes'),
      mediaA: media(g.pontos, 'media')
    }));
    return porSubitem
      ? lista.sort((a, b) => a.chave.localeCompare(b.chave))
      : lista.sort((a, b) => AREAS.indexOf(a.chave) - AREAS.indexOf(b.chave));
  })();
  const opcoesGrafico = (g) => ({ series: g.eixos.map((e) => ({ symbol: estiloEixo[e]?.forma ?? 'circle' })) });
  $: naPrioridade = grupos
    .flatMap((g) =>
      g.pontos.length > 1 ? g.pontos.filter((p) => Number(p.questoes) > g.mediaQ && Number(p.media) < g.mediaA) : []
    )
    .sort((a, b) => b.erros_esperados - a.erros_esperados);
  const pct = (v) => Math.round(Number(v) * 100) + '%';
  const umDecimal = (v) => Number(v).toFixed(1).replace('.', ',');
  const verSubitens = (p) => escolher('itens', [p.id_item]);
</script>

O gabarito comentado da UERJ publica o percentual de candidatos que acertaram cada questão. Aqui ele é cruzado com a
frequência de cada conteúdo, para mostrar onde vale mais a pena estudar: o que **cai muito e tem poucos acertos**.

<Alert status="info">
O percentual não existe para todas as questões, e a falta é da fonte oficial: o gabarito comentado de 2021 não tem o
campo, o de 2024-2 traz o campo em branco e o de 2027-2 não o publica. Faltam também as anuladas e algumas questões de
2020-2 e 2022-1. Essas questões ficam fora das médias.
</Alert>

```sql hierarquia
select distinct area, id_eixo, eixo, id_item, item from uerj.dificuldade where nivel = 'item'
```

<div class="filtros">
  <Filtro titulo="Área" opcoes={opc.areas ?? []} selecionados={sel?.areas ?? []} on:change={(e) => escolher('areas', e.detail)} />
  <span class="passo" aria-hidden="true">›</span>
  <Filtro titulo="Eixo" opcoes={opc.eixos ?? []} selecionados={sel?.eixos ?? []} on:change={(e) => escolher('eixos', e.detail)} />
  <span class="passo" aria-hidden="true">›</span>
  <Filtro titulo="Item" opcoes={opc.itens ?? []} selecionados={sel?.itens ?? []} on:change={(e) => escolher('itens', e.detail)} />
  <Dropdown name=minimo title="Mínimo de questões" defaultValue=3>
    <DropdownOption value=1 valueLabel="todas" />
    <DropdownOption value=3 valueLabel="3 ou mais" />
    <DropdownOption value=5 valueLabel="5 ou mais" />
    <DropdownOption value=10 valueLabel="10 ou mais" />
  </Dropdown>
  <button class="limpar" on:click={limparFiltros}>Limpar filtros</button>
</div>

Os filtros valem para a página inteira. O mínimo de questões tira da conta itens e subitens com poucas questões, cuja
média de acertos é instável.

```sql itens
select
    d.rotulo as item,
    d.area,
    d.eixo,
    d.id_item,
    d.qtd_questoes as questoes_com_percentual,
    r.qtd_questoes as questoes,
    d.media_acertos / 100 as media,
    d.mediana_acertos / 100 as mediana,
    d.min_acertos / 100 as minimo,
    d.max_acertos / 100 as maximo,
    r.qtd_questoes * (1 - d.media_acertos / 100) as erros_esperados
from uerj.dificuldade as d
inner join uerj.recorrencia as r on r.nivel = 'item' and r.id_conteudo = d.id_conteudo
where d.nivel = 'item'
    and d.area in ${inputs.areas.value}
    and d.id_eixo in ${inputs.eixos.value}
    and d.id_item in ${inputs.itens.value}
    and d.qtd_questoes >= ${inputs.minimo.value}
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

Quanto mais à direita, mais o conteúdo cai; quanto mais embaixo, menos os candidatos acertam. Cada eixo tem uma cor e
um formato de ponto; passe o mouse sobre um ponto para ver o nome.

<p class="nivel-atual">
  {#if porSubitem}
    Cada ponto é um <b>subitem</b>, com um gráfico por item escolhido. Para voltar aos itens, use "Selecionar todos" no
    filtro Item.
  {:else}
    Cada ponto é um <b>item</b>, com um gráfico por área. Para ver os subitens, escolha um ou mais itens no filtro Item
    ou clique em "ver subitens" na lista abaixo dos gráficos.
  {/if}
</p>

```sql dispersao
select
    d.nivel,
    d.id_conteudo,
    d.area,
    d.id_eixo,
    d.eixo,
    d.id_item,
    d.item,
    d.rotulo,
    r.qtd_questoes as questoes,
    d.media_acertos / 100 as media,
    r.qtd_questoes * (1 - d.media_acertos / 100) as erros_esperados
from uerj.dificuldade as d
inner join uerj.recorrencia as r on r.nivel = d.nivel and r.id_conteudo = d.id_conteudo
where d.area in ${inputs.areas.value}
    and d.id_eixo in ${inputs.eixos.value}
    and d.id_item in ${inputs.itens.value}
    and d.qtd_questoes >= ${inputs.minimo.value}
```

<div class="multiplos">
{#each grupos as g (g.chave)}
  <div>
    <p class="multiplo-titulo">{g.titulo}{#if g.sub}<span>{g.sub}</span>{/if}</p>
    <ul class="eixos">
      {#each g.eixos as e (e)}
        <li>
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" style={'fill: hsl(var(--twc-' + (estiloEixo[e]?.cor ?? 'eixo-1') + '))'}>
            {#if estiloEixo[e]?.forma === 'rect'}<rect x="1.5" y="1.5" width="9" height="9" />
            {:else if estiloEixo[e]?.forma === 'triangle'}<polygon points="6,1 11,11 1,11" />
            {:else if estiloEixo[e]?.forma === 'diamond'}<polygon points="6,0.5 11.5,6 6,11.5 0.5,6" />
            {:else}<circle cx="6" cy="6" r="5" />{/if}
          </svg>
          {e}
        </li>
      {/each}
    </ul>
    <ScatterPlot
      data={g.pontos}
      x=questoes
      y=media
      series=eixo
      seriesOrder={g.eixos}
      seriesColors={coresEixos}
      echartsOptions={opcoesGrafico(g)}
      legend=false
      tooltipTitle=rotulo
      yFmt=pct0
      yMin=0
      yMax=1
      xMin=0
      pointSize=11
      xAxisTitle="Questões desde 2016"
      yAxisTitle="Média de acertos"
      chartAreaHeight=220
    >
      {#if g.pontos.length > 1}
        <ReferenceArea xMin={g.mediaQ} yMin={0} yMax={g.mediaA} color="accent" label="prioridade" labelPosition="bottomRight" />
        <ReferenceLine y={g.mediaA} hideValue=true lineType=dashed />
        <ReferenceLine x={g.mediaQ} hideValue=true lineType=dashed />
      {/if}
    </ScatterPlot>
  </div>
{:else}
  <p>Nenhum conteúdo com percentual publicado nesta seleção. Diminua o mínimo de questões ou use "Limpar filtros".</p>
{/each}
</div>

<div class="legenda" aria-label="Legenda dos gráficos">
  <span><svg width="28" height="10" aria-hidden="true"><line x1="0" y1="5" x2="28" y2="5" class="tracejado" /></svg>
    <span>média do gráfico: a linha em pé marca o número médio de questões; a deitada, a média de acertos</span></span>
  <span><svg width="28" height="12" aria-hidden="true"><rect width="28" height="12" class="faixa" /></svg>
    <span><b>prioridade</b>: cai mais que a média e tem menos acertos que a média. Comece por eles.</span></span>
</div>

### Na faixa de prioridade

{#if naPrioridade.length}
<div class="tabela-prioridade">
<table>
  <thead>
    <tr>
      <th>{porSubitem ? 'Subitem' : 'Item'}</th>
      <th>{porSubitem ? 'Item' : 'Eixo'}</th>
      <th class="num">Questões</th>
      <th class="num">Acertos</th>
      <th class="num" title="Questões × taxa de erro: quantas dessas questões um candidato típico errou">Erradas por um candidato típico</th>
      {#if !porSubitem}<th><span class="sr">Detalhar</span></th>{/if}
    </tr>
  </thead>
  <tbody>
    {#each naPrioridade as p (p.id_conteudo)}
      <tr>
        <td>{p.rotulo}</td>
        <td>{porSubitem ? p.item : p.eixo}</td>
        <td class="num">{p.questoes}</td>
        <td class="num">{pct(p.media)}</td>
        <td class="num">{umDecimal(p.erros_esperados)}</td>
        {#if !porSubitem}<td><button class="ver" on:click={() => verSubitens(p)}>ver subitens</button></td>{/if}
      </tr>
    {/each}
  </tbody>
</table>
</div>
{:else}
<p class="vazio">Nenhum conteúdo na faixa de prioridade nesta seleção.</p>
{/if}

## Todos os itens

<DataTable data={itens} rows=10 search=true sort="media" emptySet=pass emptyMessage="Nenhum item nesta seleção.">
  <Column id=item title="Item" wrap=true />
  <Column id=eixo title="Eixo" wrap=true />
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
select id_questao, area, classificacao, percentual_acertos / 100 as acertos, url_prova, url_comentario
from uerj.questoes
where percentual_acertos is not null
    and id_questao in (
        select id_questao
        from uerj.classificacoes
        where area in ${inputs.areas.value} and id_eixo in ${inputs.eixos.value} and id_item in ${inputs.itens.value}
    )
order by percentual_acertos
limit 25
```

<DataTable data={questoes_dificeis} rows=10 emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=area title="Área" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_comentario title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

## Média de acertos por exame

```sql por_exame
select e.rotulo_curto, e.id_exame, avg(q.percentual_acertos) / 100 as media
from uerj.questoes as q
inner join uerj.exames as e using (id_exame)
where q.percentual_acertos is not null
    and q.id_questao in (
        select id_questao
        from uerj.classificacoes
        where area in ${inputs.areas.value} and id_eixo in ${inputs.eixos.value} and id_item in ${inputs.itens.value}
    )
group by all
order by e.id_exame
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

A média é a das questões da seleção dos filtros. Faltam 2021, 2024-2 e 2027-2, que não têm percentual
publicado.

<style>
  .multiplos { display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); gap: 0.5rem 2rem; }
  .legenda { display: flex; flex-direction: column; gap: 0.35rem; margin: 0.25rem 0 0.5rem; font-size: 0.85rem;
             color: hsl(var(--twc-base-content-muted)); }
  .legenda > span { display: flex; align-items: center; gap: 0.6rem; }
  .legenda svg { flex: none; }
  .tracejado { stroke: hsl(var(--twc-base-content-muted)); stroke-width: 1.3; stroke-dasharray: 4 3; }
  .faixa { fill: hsl(var(--twc-accent) / 0.25); }
  .multiplo-titulo { margin: 0.75rem 0 0; font-weight: 650; color: hsl(var(--twc-base-heading)); }
  .multiplo-titulo span { margin-left: 0.4rem; font-size: 0.8rem; font-weight: 400; color: hsl(var(--twc-base-content-muted)); }
  .eixos { display: flex; flex-wrap: wrap; gap: 0.15rem 0.9rem; margin: 0.2rem 0 0; padding: 0; list-style: none;
           font-size: 0.8rem; color: hsl(var(--twc-base-content)); }
  .eixos li { display: inline-flex; align-items: center; gap: 0.35rem; }
  .nivel-atual { max-width: none; font-size: 0.9rem; padding: 0.5rem 0.75rem; border-left: 3px solid hsl(var(--twc-primary));
                 background: hsl(var(--twc-primary) / 0.06); }
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.5rem; align-items: center; margin: 0.5rem 0 0.5rem; }
  .filtros :global(p) { margin: 0; }
  .passo { color: hsl(var(--twc-primary)); font-size: 1.2rem; }
  .limpar { padding: 0.35rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
            border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .limpar:hover, .ver:hover { background: hsl(var(--twc-primary) / 0.08); }
  .tabela-prioridade { overflow-x: auto; }
  .tabela-prioridade table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  .tabela-prioridade th { text-align: left; font-weight: 650; padding: 0.4rem 0.5rem;
                          border-bottom: 1px solid hsl(var(--twc-base-content) / 0.3); color: hsl(var(--twc-base-heading)); }
  .tabela-prioridade td { padding: 0.4rem 0.5rem; border-bottom: 1px solid hsl(var(--twc-base-content) / 0.1); }
  .tabela-prioridade .num { text-align: right; font-variant-numeric: tabular-nums; }
  .ver { white-space: nowrap; padding: 0.2rem 0.55rem; border-radius: 5px; font-size: 0.8rem; font-weight: 600;
         border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .vazio { color: hsl(var(--twc-base-content-muted)); }
</style>
