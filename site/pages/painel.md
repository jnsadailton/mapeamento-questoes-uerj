---
title: O que mais cai
description: Escolha vestibulares, exames, áreas, disciplinas, eixos e itens e veja o que mais caiu em cada nível do programa.
sidebar_position: 3
---

<script>
  import { AREAS, gravarInputs, criarCascata, linhasDe, naOrdem, paraInput, unicas } from '$lib/filtros.js';
  import { barrasDeitadas } from '$lib/graficos.js';
  const opcoesBarras = barrasDeitadas();

  // Cor fixa por área (tokens do tema, ver docs/paleta-de-cores.md)
  const coresArea = {
    'Linguagens': 'area-lin',
    'Matemática': 'area-mat',
    'Ciências da Natureza': 'area-cnt',
    'Ciências Humanas': 'area-chs'
  };
  const ordemAreas = AREAS;

  // Área › Disciplina › Eixo › Item: cada filtro só oferece o que existe dentro do que está marcado acima, e volta a
  // "todos" quando um filtro de cima muda.
  const conteudo = criarCascata([
    { nome: 'areas', valor: 'area', ordenar: naOrdem(AREAS) },
    { nome: 'disciplinas', valor: 'disciplina' },
    { nome: 'eixos', valor: 'id_eixo', rotulo: 'eixo' },
    { nome: 'itens', valor: 'id_item', rotulo: 'item' }
  ]);
  const naOrdemDaConsulta = () => 0;

  $: hier = linhasDe(hierarquia);
  $: opcAnos = unicas(linhasDe(anos), 'ano', 'rotulo_ano', naOrdemDaConsulta);
  $: opcEtapas = unicas(linhasDe(etapas), 'etapa', 'etapa', naOrdemDaConsulta);

  let sel = null;
  function limparFiltros() {
    sel = { anos: opcAnos.map((o) => o.valor), etapas: opcEtapas.map((o) => o.valor), ...conteudo.inicial(hier) };
  }
  $: if (!sel && hier.length && opcAnos.length && opcEtapas.length) limparFiltros();
  $: opc = sel ? conteudo.opcoes(hier, sel) : {};
  function escolher(nome, valores) {
    sel = nome === 'anos' || nome === 'etapas' ? { ...sel, [nome]: valores } : conteudo.escolher(hier, sel, nome, valores);
  }
  $: if (sel)
    gravarInputs(inputs_store, {
      anos: paraInput(sel.anos, opcAnos),
      etapas: paraInput(sel.etapas, opcEtapas),
      areas: paraInput(sel.areas, opc.areas),
      disciplinas: paraInput(sel.disciplinas, opc.disciplinas),
      eixos: paraInput(sel.eixos, opc.eixos),
      itens: paraInput(sel.itens, opc.itens)
    });
</script>

Monte a sua seleção e tudo abaixo se atualiza: os indicadores, os rankings de eixos, itens e subitens, os links das
provas escolhidas e, no fim da página, a lista das questões.

<Hierarquia compacto=true />

```sql anos
select distinct ano, rotulo_ano from uerj.exames order by ano desc
```

```sql etapas
select etapa, min(numero) as ordem from uerj.exames group by etapa order by ordem, etapa
```

```sql hierarquia
select distinct area, disciplina, id_eixo, eixo, id_item, item from uerj.classificacoes
```

<div class="painel-filtros">
  <div class="grupo">
    <p class="grupo-titulo">Provas</p>
    <div class="linha">
      <Filtro titulo="Vestibular" opcoes={opcAnos} selecionados={sel?.anos ?? []} on:change={(e) => escolher('anos', e.detail)} />
      <Filtro titulo="Exame" opcoes={opcEtapas} selecionados={sel?.etapas ?? []} on:change={(e) => escolher('etapas', e.detail)} />
    </div>
  </div>
  <div class="grupo">
    <p class="grupo-titulo">Conteúdo <span>cada filtro só mostra o que está dentro do anterior</span></p>
    <div class="linha">
      <Filtro titulo="Área" opcoes={opc.areas ?? []} selecionados={sel?.areas ?? []} on:change={(e) => escolher('areas', e.detail)} />
      <span class="passo" aria-hidden="true">›</span>
      <Filtro titulo="Disciplina" opcoes={opc.disciplinas ?? []} selecionados={sel?.disciplinas ?? []} on:change={(e) => escolher('disciplinas', e.detail)} />
      <span class="passo" aria-hidden="true">›</span>
      <Filtro titulo="Eixo" opcoes={opc.eixos ?? []} selecionados={sel?.eixos ?? []} on:change={(e) => escolher('eixos', e.detail)} />
      <span class="passo" aria-hidden="true">›</span>
      <Filtro titulo="Item" opcoes={opc.itens ?? []} selecionados={sel?.itens ?? []} on:change={(e) => escolher('itens', e.detail)} />
    </div>
  </div>
  <button class="limpar" on:click={limparFiltros}>Limpar filtros</button>
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
where id_exame in (select id_exame from ${sel_exames})
    and area in ${inputs.areas.value}
    and disciplina in ${inputs.disciplinas.value}
    and id_eixo in ${inputs.eixos.value}
    and id_item in ${inputs.itens.value}
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
  <BigValue data={kpis} value=exames title="Exames selecionados" emptySet=pass emptyMessage="—" valueClass="valor" />
  <BigValue data={kpis} value=questoes fmt="0" title="Questões na seleção" emptySet=pass emptyMessage="—" valueClass="valor" />
  <BigValue data={kpis} value=itens title="Itens diferentes cobrados" emptySet=pass emptyMessage="—" valueClass="valor" />
  <BigValue data={kpis} value=media_acertos fmt=pct0 title="Média de acertos" emptySet=pass emptyMessage="não publicada" valueClass="valor" />
</Grid>

{#if kpis.length && kpis[0].questoes === 0}

<Alert status="warning">Nenhuma questão nesta seleção. Use "Limpar filtros" ou escolha pelo menos uma opção em cada filtro.</Alert>

{/if}

*Questões* conta cada número de questão uma vez: as versões em espanhol, francês e inglês do mesmo número contam juntas.
Uma questão classificada em dois conteúdos conta para os dois.

## Eixos

```sql rank_eixos
select
    eixo,
    area,
    count(distinct id_exame || '-' || numero) as questoes,
    count(distinct id_exame) as exames
from ${sel_class}
group by all
order by questoes desc, eixo
```

<BarChart
  data={rank_eixos}
  x=eixo
  y=questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  swapXY=true
  echartsOptions={opcoesBarras}
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  emptySet=pass
  emptyMessage="Nenhum eixo para esta seleção."
/>

## Itens

```sql rank_itens
select
    item,
    eixo,
    area,
    count(distinct id_exame || '-' || numero) as questoes,
    count(distinct id_exame) as exames
from ${sel_class}
group by all
```

```sql rank_itens_total
select
    r.*,
    r.questoes / sum(r.questoes) over () as participacao,
    r.exames / (select count(*) from ${sel_exames}) as frequencia,
    case when length(r.item) > 50 then left(r.item, 49) || '…' else r.item end as rotulo
from ${rank_itens} as r
order by questoes desc, exames desc, item
```

```sql top_itens
select * from ${rank_itens_total} limit 15
```

<BarChart
  data={top_itens}
  x=rotulo
  y=questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  swapXY=true
  echartsOptions={opcoesBarras}
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  chartAreaHeight=420
  emptySet=pass
  emptyMessage="Nenhum item para esta seleção."
/>

```sql concentracao
with r as (
    select
        questoes,
        sum(questoes) over (order by questoes desc, item rows unbounded preceding) as acumulado,
        sum(questoes) over () as total
    from ${rank_itens}
)
select
    count(*) filter (where acumulado - questoes < total * 0.5) as para_metade,
    count(*) as distintos
from r
having count(*) > 0
```

{#if concentracao.length && concentracao[0].distintos > 1}

<Alert status="info">
<b>Concentração:</b> {concentracao[0].para_metade} dos {concentracao[0].distintos} itens cobrados nesta seleção somam
metade das questões. Comece por eles.
</Alert>

{/if}

<DataTable data={rank_itens_total} rows=10 search=true emptySet=pass emptyMessage="Nenhum item para esta seleção.">
  <Column id=item title="Item" wrap=true />
  <Column id=eixo title="Eixo" wrap=true />
  <Column id=questoes title="Questões" contentType=bar barColor="#9cc8f0" />
  <Column id=participacao title="% das questões" fmt=pct0 />
  <Column id=exames title="Exames em que caiu" />
  <Column id=frequencia title="% dos exames" fmt=pct0 />
</DataTable>

## Subitens

Os subitens dos itens selecionados. Para ver os subitens de um item só, escolha esse item no filtro **Item**.

```sql rank_subitens
select
    subitem,
    item,
    area,
    count(distinct id_exame || '-' || numero) as questoes,
    count(distinct id_exame) as exames
from ${sel_class}
where id_subitem is not null
group by all
```

```sql rank_subitens_total
select
    r.*,
    r.exames / (select count(*) from ${sel_exames}) as frequencia,
    -- o mesmo subitem pode existir em itens diferentes: o rótulo do gráfico ganha o item entre parênteses
    case when count(*) over (partition by r.subitem) > 1 then r.subitem || ' (' || r.item || ')' else r.subitem end
        as rotulo_completo
from ${rank_subitens} as r
order by questoes desc, exames desc, subitem
```

```sql top_subitens
select
    *,
    case when length(rotulo_completo) > 50 then left(rotulo_completo, 49) || '…' else rotulo_completo end as rotulo
from ${rank_subitens_total}
limit 15
```

<BarChart
  data={top_subitens}
  x=rotulo
  y=questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  swapXY=true
  echartsOptions={opcoesBarras}
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  chartAreaHeight=420
  emptySet=pass
  emptyMessage="Nenhum subitem para esta seleção."
/>

<DataTable data={rank_subitens_total} rows=10 search=true emptySet=pass emptyMessage="Nenhum subitem para esta seleção.">
  <Column id=subitem title="Subitem" wrap=true />
  <Column id=item title="Item" wrap=true />
  <Column id=questoes title="Questões" contentType=bar barColor="#9cc8f0" />
  <Column id=exames title="Exames em que caiu" />
  <Column id=frequencia title="% dos exames" fmt=pct0 />
</DataTable>

Quando o gabarito comentado só informa o item, a questão conta para o item mas não aparece entre os subitens.

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
  echartsOptions={opcoesBarras}
  sort=false
  labels=true
  seriesLabels=false
  stackTotalLabel=true
  xAxisTitle=" "
  yAxisTitle="Questões"
  emptySet=pass
  emptyMessage="Nenhuma disciplina para esta seleção."
/>

Ciências Humanas aparece inteira porque os editais não separam Geografia e História.

## As provas selecionadas

Links para os PDFs oficiais de cada exame da seleção, no site da UERJ. Os conteúdos programáticos de 2016 a 2018
ficam no servidor antigo da universidade, cujo certificado de segurança venceu: o navegador pode mostrar um aviso antes
de abrir (o arquivo é o oficial, conferido pelo projeto).

<DataTable data={sel_exames} rows=12 emptySet=pass emptyMessage="Nenhum exame selecionado.">
  <Column id=nome title="Exame" />
  <Column id=data_aplicacao title="Aplicação" fmt="dd/mm/yyyy" />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_gabarito title="Gabarito" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_gabarito_comentado title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_conteudo_programatico title="Conteúdo programático" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

## As questões da seleção

Todas as questões que entram nos números acima. Abra a prova direto na página da questão ou o gabarito comentado
oficial, com a resolução e a classificação.

```sql questoes_sel
select
    q.id_questao,
    q.classificacao,
    q.resposta,
    q.percentual_acertos / 100 as acertos,
    q.observacoes,
    q.url_prova,
    q.url_comentario
from uerj.questoes as q
where q.id_questao in (select id_questao from ${sel_class})
order by q.id_exame desc, q.numero, q.idioma nulls first
```

<p class="contagem">{questoes_sel.length} {questoes_sel.length === 1 ? 'versão de questão' : 'versões de questão'} na seleção (no bloco de língua estrangeira, cada idioma é uma versão).</p>

<DataTable data={questoes_sel} rows=15 search=true emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=resposta title="Gabarito" />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=observacoes title="Adendo do projeto" wrap=true />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_comentario title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

<style>
  .painel-filtros { display: flex; flex-direction: column; gap: 0.6rem; margin: 0.5rem 0 1.5rem; padding: 0.9rem 0 1rem;
                    border-top: 2px solid hsl(var(--twc-base-heading)); border-bottom: 1px solid hsl(var(--twc-base-content) / 0.15); }
  .grupo-titulo { margin: 0; font-size: 0.9rem; font-weight: 650; color: hsl(var(--twc-base-heading)); }
  .grupo-titulo span { margin-left: 0.5rem; font-size: 0.82rem; font-weight: 400; color: hsl(var(--twc-base-content-muted)); }
  .linha { display: flex; flex-wrap: wrap; align-items: center; gap: 0 0.35rem; }
  .linha :global(p) { margin: 0; }
  .passo { color: hsl(var(--twc-primary)); font-size: 1.2rem; margin: 0 0.1rem; }
  .limpar { align-self: flex-start; padding: 0.35rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
            border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .limpar:hover { background: hsl(var(--twc-primary) / 0.08); }
  .contagem { font-size: 0.85rem; color: hsl(var(--twc-base-content-muted)); }
</style>
