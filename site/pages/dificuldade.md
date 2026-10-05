---
title: Dificuldade
description: Onde os candidatos mais erram e o que é um diferencial saber, por item e por subitem.
sidebar_position: 6
---

<script>
  import { AREAS, criarCascata, gravarInputs, linhasDe, naOrdem, paraInput } from '$lib/filtros.js';
  import { barrasDeitadas } from '$lib/graficos.js';
  const opcoesBarras = barrasDeitadas();

  // Área › Disciplina › Eixo › Item: valem para a página inteira. A disciplina é a da classificação (em Linguagens,
  // Língua Estrangeira separa o bloco de espanhol, francês e inglês das questões em português).
  const conteudo = criarCascata([
    { nome: 'areas', valor: 'area', ordenar: naOrdem(AREAS) },
    { nome: 'disciplinas', valor: 'disciplina' },
    { nome: 'eixos', valor: 'id_eixo', rotulo: 'eixo' },
    { nome: 'itens', valor: 'id_item', rotulo: 'item' }
  ]);
  $: hier = linhasDe(hierarquia);
  let sel = null;
  $: if (!sel && hier.length) sel = conteudo.inicial(hier);
  $: opc = sel ? conteudo.opcoes(hier, sel) : {};
  const escolher = (nome, valores) => (sel = conteudo.escolher(hier, sel, nome, valores));
  const limparFiltros = () => (sel = conteudo.inicial(hier));

  // Nível do detalhe: com todos os itens marcados, a página mostra itens; com só alguns itens marcados, mostra os
  // subitens deles. Toda a página (pontos perdidos, gráficos, listas) segue o mesmo nível.
  $: porSubitem = !!sel && (opc.itens ?? []).length > 0 && sel.itens.length < opc.itens.length;
  $: nivel = porSubitem ? 'subitem' : 'item';
  $: Nivel = porSubitem ? 'Subitem' : 'Item';
  $: if (sel)
    gravarInputs(inputs_store, {
      areas: paraInput(sel.areas, opc.areas),
      disciplinas: paraInput(sel.disciplinas, opc.disciplinas),
      eixos: paraInput(sel.eixos, opc.eixos),
      itens: paraInput(sel.itens, opc.itens),
      niveis_dificuldade: paraInput([nivel])
    });
  $: itensEscolhidos = porSubitem ? (opc.itens ?? []).filter((o) => sel.itens.includes(o.valor)).map((o) => o.rotulo) : [];
  const verSubitensDe = (idItem) => {
    if (!idItem) return;
    escolher('itens', [idItem]);
    // leva o leitor de volta ao começo dos gráficos, onde o detalhe aparece
    document.getElementById('frequencia-acertos')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  const voltarAosItens = () => escolher('itens', (opc.itens ?? []).map((o) => o.valor));

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

  // Gráficos pequenos: um por área (itens) ou um por item escolhido (subitens).
  $: pontos = linhasDe(conteudos).filter((r) => r.nivel === nivel);
  const media = (l, campo) => l.reduce((t, r) => t + Number(r[campo]), 0) / l.length;
  const porId = (a, b) => (estiloEixo[a]?.id ?? '').localeCompare(estiloEixo[b]?.id ?? '');
  $: grupos = (() => {
    const mapa = new Map();
    for (const r of pontos) {
      const chave = porSubitem ? r.id_item : r.area;
      if (!mapa.has(chave))
        mapa.set(chave, {
          chave,
          titulo: porSubitem ? 'Subitens de ' + r.item : r.area,
          sub: porSubitem ? 'eixo ' + r.eixo : '',
          pontos: []
        });
      mapa.get(chave).pontos.push(r);
    }
    const lista = [...mapa.values()].map((g) => ({
      ...g,
      eixos: [...new Set(g.pontos.map((p) => p.eixo))].sort(porId),
      itens: porSubitem ? [] : [...g.pontos].sort((a, b) => a.conteudo.localeCompare(b.conteudo, 'pt')),
      mediaQ: media(g.pontos, 'questoes'),
      mediaA: media(g.pontos, 'media')
    }));
    return porSubitem
      ? lista.sort((a, b) => a.chave.localeCompare(b.chave))
      : lista.sort((a, b) => AREAS.indexOf(a.chave) - AREAS.indexOf(b.chave));
  })();
  const opcoesGrafico = (g) => ({ series: g.eixos.map((e) => ({ symbol: estiloEixo[e]?.forma ?? 'circle' })) });
  $: naFaixaDiferencial = grupos
    .flatMap((g) =>
      g.pontos.length > 1 ? g.pontos.filter((p) => Number(p.questoes) > g.mediaQ && Number(p.media) < g.mediaA) : []
    )
    .sort((a, b) => b.erros_esperados - a.erros_esperados);
  const pct = (v) => Math.round(Number(v) * 100) + '%';
  const umDecimal = (v) => Number(v).toFixed(1).replace('.', ',');
</script>

O gabarito comentado da UERJ publica o percentual de candidatos que acertaram cada questão. Esta página cruza esse
percentual com a frequência de cada conteúdo, para mostrar onde vale mais a pena estudar: o que **cai muito e tem
poucos acertos**. Dá para ver por **item** e descer até os **subitens** de cada item.

<AnoVestibular />

<ol class="como-usar">
  <li>Escolha a área, a disciplina, o eixo ou o item nos filtros, ou deixe tudo marcado.</li>
  <li>Veja o que está na faixa de <b>diferencial</b> do gráfico de frequência × acertos e na lista logo abaixo dele:
  conteúdos que caem bastante e que a maioria erra.</li>
  <li>Para ver os <b>subitens</b> de um item, toque em "ver subitens" na lista, use "Ver os subitens de…" embaixo de cada
  gráfico ou marque o item no filtro Item.</li>
</ol>

```sql hierarquia
select distinct area, disciplina, id_eixo, eixo, id_item, item
from uerj.classificacoes
where percentual_acertos is not null and not anulada
```

<div class="filtros">
  <Filtro titulo="Área" opcoes={opc.areas ?? []} selecionados={sel?.areas ?? []} on:change={(e) => escolher('areas', e.detail)} />
  <span class="passo" aria-hidden="true">›</span>
  <Filtro titulo="Disciplina" opcoes={opc.disciplinas ?? []} selecionados={sel?.disciplinas ?? []} on:change={(e) => escolher('disciplinas', e.detail)} />
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

<div class="nivel" role="status">
  <span class="nivel-rotulo">Detalhe:</span>
  {#if porSubitem}
    <button class="nivel-passo" on:click={voltarAosItens}>Itens</button>
    <span class="nivel-seta" aria-hidden="true">›</span>
    <span class="nivel-passo atual">Subitens de {itensEscolhidos.length === 1 ? itensEscolhidos[0] : itensEscolhidos.length + ' itens'}</span>
    <button class="voltar" on:click={voltarAosItens}>Voltar para os itens</button>
  {:else}
    <span class="nivel-passo atual">Itens</span>
    <span class="nivel-seta" aria-hidden="true">›</span>
    <span class="nivel-passo futuro">Subitens: escolha um item</span>
  {/if}
</div>

<Alert status="info">
Não há percentual de acertos para 2021, 2024-2 e 2027-2: os gabaritos comentados desses exames não trazem essa
informação. Faltam também as anuladas e algumas questões de 2020-2 e 2022-1. Essas questões ficam fora das médias. O mínimo de questões tira da conta conteúdos com poucas questões,
cuja média é instável.
</Alert>

```sql conteudos
-- Frequência e acertos de cada conteúdo, contando só as questões da seleção (a disciplina Língua Estrangeira, por
-- exemplo, usa só as versões em espanhol, francês e inglês). Frequência: números de questão, com as versões de língua
-- estrangeira contando uma vez. Acertos: cada versão com percentual publicado é um ponto; anuladas ficam de fora.
with selecao as (
    select *
    from uerj.classificacoes
    where area in ${inputs.areas.value}
        and disciplina in ${inputs.disciplinas.value}
        and id_eixo in ${inputs.eixos.value}
        and id_item in ${inputs.itens.value}
),

pontos as (
    select 'item' as nivel, id_item as id_conteudo, id_exame, numero, id_questao, percentual_acertos, anulada from selecao
    union all
    select 'subitem', id_subitem, id_exame, numero, id_questao, percentual_acertos, anulada
    from selecao
    where id_subitem is not null
),

frequencia as (
    select nivel, id_conteudo, cast(count(distinct id_exame || '-' || cast(numero as varchar)) as integer) as questoes
    from pontos
    group by all
),

acertos as (
    select
        nivel,
        id_conteudo,
        cast(count(*) as integer) as questoes_com_percentual,
        avg(p) as media,
        median(p) as mediana,
        min(p) as minimo,
        max(p) as maximo
    from (
        select distinct nivel, id_conteudo, id_questao, percentual_acertos / 100 as p
        from pontos
        where percentual_acertos is not null and not anulada
    )
    group by all
)

select
    a.nivel,
    a.id_conteudo,
    coalesce(c.subitem, c.item) as conteudo,
    c.area,
    c.eixo,
    c.id_item,
    c.item,
    case when a.nivel = 'subitem' then c.item else c.eixo end as acima,
    a.questoes_com_percentual,
    f.questoes,
    a.media,
    a.mediana,
    a.minimo,
    a.maximo,
    f.questoes * (1 - a.media) as erros_esperados
from acertos as a
inner join frequencia as f using (nivel, id_conteudo)
inner join uerj.conteudo as c on c.id_conteudo = a.id_conteudo
where a.nivel in ${inputs.niveis_dificuldade.value}
    and a.questoes_com_percentual >= ${inputs.minimo.value}
```

## Onde mais se perde ponto

Para cada {nivel}, as questões desde 2016 vezes a taxa de erro média: quantas dessas questões um candidato típico
errou. São os pontos que a maioria deixa na prova.

```sql pontos_perdidos
select
    case when length(r) > 48 then left(r, 47) || '…' else r end as rotulo,
    area,
    erros_esperados
from (
    select
        -- o mesmo subitem pode existir em itens diferentes: o nome ganha o item entre parênteses
        case when count(*) over (partition by conteudo) > 1 then conteudo || ' (' || item || ')' else conteudo end as r,
        area,
        erros_esperados
    from ${conteudos}
)
order by erros_esperados desc
limit 15
```

<BarChart
  data={pontos_perdidos}
  x=rotulo
  y=erros_esperados
  series=area
  seriesOrder={['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas']}
  seriesColors={{'Linguagens': 'area-lin', 'Matemática': 'area-mat', 'Ciências da Natureza': 'area-cnt', 'Ciências Humanas': 'area-chs'}}
  swapXY=true
  echartsOptions={opcoesBarras}
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
  emptyMessage="Nenhum conteúdo com percentual publicado nesta seleção."
/>

<h2 class="markdown" id="frequencia-acertos">Frequência × acertos</h2>

Quanto mais à direita, mais o conteúdo cai; quanto mais embaixo, menos os candidatos acertam. Cada eixo tem uma cor e
um formato de ponto. Toque num ponto (ou passe o mouse) para ver o nome.

<div class="multiplos">
{#each grupos as g (g.chave)}
  <div class="multiplo">
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
      tooltipTitle=conteudo
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
        <ReferenceArea xMin={g.mediaQ} yMin={0} yMax={g.mediaA} color="accent" label="diferencial" labelPosition="bottomRight" />
        <ReferenceLine y={g.mediaA} hideValue=true lineType=dashed />
        <ReferenceLine x={g.mediaQ} hideValue=true lineType=dashed />
      {/if}
    </ScatterPlot>
    {#if !porSubitem}
      <label class="detalhar">
        <span>Ver os subitens de…</span>
        <select on:change={(e) => verSubitensDe(e.currentTarget.value)}>
          <option value="">um item de {g.titulo}</option>
          {#each g.itens as it (it.id_item)}<option value={it.id_item}>{it.conteudo}</option>{/each}
        </select>
      </label>
    {/if}
  </div>
{:else}
  <p>Nenhum conteúdo com percentual publicado nesta seleção. Diminua o mínimo de questões ou use "Limpar filtros".</p>
{/each}
</div>

<div class="legenda" aria-label="Legenda dos gráficos">
  <span><svg width="28" height="10" aria-hidden="true"><line x1="0" y1="5" x2="28" y2="5" class="tracejado" /></svg>
    <span>média do gráfico: a linha em pé marca o número médio de questões; a deitada, a média de acertos</span></span>
  <span><svg width="28" height="12" aria-hidden="true"><rect width="28" height="12" class="faixa" /></svg>
    <span><b>diferencial</b>: cai mais que a média e tem menos acertos que a média. Saber esses conteúdos é um
    diferencial, porque a maioria erra.</span></span>
</div>

### Conteúdos que são um diferencial

{#if naFaixaDiferencial.length}
<div class="tabela-diferencial">
<table>
  <thead>
    <tr>
      <th>{Nivel}</th>
      <th class="opcional">{porSubitem ? 'Item' : 'Eixo'}</th>
      <th class="num">Questões</th>
      <th class="num">Acertos</th>
      <th class="num" title="Questões × taxa de erro: quantas dessas questões um candidato típico errou">Erradas*</th>
      {#if !porSubitem}<th><span class="sr">Ver subitens</span></th>{/if}
    </tr>
  </thead>
  <tbody>
    {#each naFaixaDiferencial as p (p.id_conteudo)}
      <tr>
        <td>{p.conteudo}<span class="acima-celular">{porSubitem ? p.item : p.eixo}</span></td>
        <td class="opcional">{porSubitem ? p.item : p.eixo}</td>
        <td class="num">{p.questoes}</td>
        <td class="num">{pct(p.media)}</td>
        <td class="num">{umDecimal(p.erros_esperados)}</td>
        {#if !porSubitem}<td><button class="ver" on:click={() => verSubitensDe(p.id_item)}>ver subitens</button></td>{/if}
      </tr>
    {/each}
  </tbody>
</table>
</div>
<p class="nota">* Erradas: quantas dessas questões um candidato típico errou (questões × taxa de erro).</p>
{:else}
<p class="vazio">Nenhum conteúdo na faixa de diferencial nesta seleção.</p>
{/if}

## {porSubitem ? 'Todos os subitens' : 'Todos os itens'}

<DataTable data={conteudos} rows=10 search=true sort="media" emptySet=pass emptyMessage="Nada nesta seleção.">
  <Column id=conteudo title={Nivel} wrap=true />
  <Column id=acima title={porSubitem ? 'Item' : 'Eixo'} wrap=true />
  <Column id=questoes title="Questões" />
  <Column id=media title="Média de acertos" fmt=pct0 contentType=bar barColor="#9cc8f0" />
  <Column id=mediana title="Mediana" fmt=pct0 />
  <Column id=minimo title="Mínimo" fmt=pct0 />
  <Column id=maximo title="Máximo" fmt=pct0 />
</DataTable>

Cada versão de questão com percentual publicado é um ponto da média; no bloco de língua estrangeira, cada idioma conta
separadamente. Com uma disciplina marcada, as questões e as médias são só as dela: em Linguagens, Língua Portuguesa e
Literatura são as questões em português, e Língua Estrangeira, o bloco de espanhol, francês e inglês.

## As questões mais difíceis

```sql questoes_dificeis
select id_questao, area, classificacao, percentual_acertos / 100 as acertos, url_prova, url_comentario
from uerj.questoes
where percentual_acertos is not null
    and id_questao in (
        select id_questao
        from uerj.classificacoes
        where area in ${inputs.areas.value} and disciplina in ${inputs.disciplinas.value}
            and id_eixo in ${inputs.eixos.value} and id_item in ${inputs.itens.value}
    )
order by percentual_acertos
limit 25
```

<DataTable data={questoes_dificeis} rows=10 emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_comentario title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=area title="Área" />
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
        where area in ${inputs.areas.value} and disciplina in ${inputs.disciplinas.value}
            and id_eixo in ${inputs.eixos.value} and id_item in ${inputs.itens.value}
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
  xAxisTitle="Exame (ano do vestibular)"
  yAxisTitle="Média de acertos"
  emptySet=pass
/>

A média é a das questões da seleção dos filtros. Faltam 2021, 2024-2 e 2027-2, porque não há percentual de acertos
desses exames.

<style>
  .como-usar { list-style: decimal; max-width: 72ch; margin: 0.5rem 0 1rem; padding-left: 1.4rem; font-size: 0.95rem; line-height: 1.55; }
  .como-usar li { margin: 0.2rem 0; }
  .como-usar li::marker { font-family: var(--fonte-titulo); font-weight: 600; color: hsl(var(--twc-primary)); }
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.5rem; align-items: center; margin: 0.5rem 0; }
  .filtros :global(p) { margin: 0; }
  .passo { color: hsl(var(--twc-primary)); font-size: 1.2rem; }
  .limpar { padding: 0.35rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
            border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .limpar:hover, .ver:hover, .voltar:hover { background: hsl(var(--twc-primary) / 0.08); }

  .nivel { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem 0.5rem; margin: 0.75rem 0 1rem;
           padding: 0.6rem 0.8rem; border-radius: 8px; background: hsl(var(--twc-primary) / 0.07); font-size: 0.9rem; }
  .nivel-rotulo { font-weight: 650; color: hsl(var(--twc-base-heading)); }
  .nivel-passo { padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.85rem; background: transparent;
                 color: hsl(var(--twc-primary)); border: 1px solid hsl(var(--twc-primary) / 0.4); }
  .nivel-passo.atual { background: hsl(var(--twc-primary)); color: hsl(var(--twc-primary-content)); border-color: transparent;
                       font-weight: 600; }
  .nivel-passo.futuro { border-style: dashed; color: hsl(var(--twc-base-content-muted)); }
  .nivel-seta { color: hsl(var(--twc-primary)); }
  .voltar { margin-left: auto; padding: 0.3rem 0.7rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
            border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: hsl(var(--twc-base-100)); }

  .multiplos { display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); gap: 0.5rem 2rem; }
  .multiplo { min-width: 0; }
  .multiplo-titulo { margin: 0.75rem 0 0; font-weight: 650; color: hsl(var(--twc-base-heading)); }
  .multiplo-titulo span { margin-left: 0.4rem; font-size: 0.8rem; font-weight: 400; color: hsl(var(--twc-base-content-muted)); }
  .eixos { display: flex; flex-wrap: wrap; gap: 0.15rem 0.9rem; margin: 0.2rem 0 0; padding: 0; list-style: none;
           font-size: 0.8rem; color: hsl(var(--twc-base-content)); }
  .eixos li { display: inline-flex; align-items: center; gap: 0.35rem; }
  .detalhar { display: flex; flex-wrap: wrap; align-items: center; gap: 0.25rem 0.5rem; margin: 0 0 0.5rem;
              font-size: 0.85rem; font-weight: 600; color: hsl(var(--twc-base-heading)); }
  .detalhar select { flex: 1 1 12rem; min-width: 0; height: 2.1rem; padding: 0 0.5rem; border-radius: 6px; font-size: 0.85rem;
                     font-weight: 400; border: 1px solid hsl(var(--twc-primary) / 0.5); background: hsl(var(--twc-base-100));
                     color: hsl(var(--twc-base-content)); }

  .legenda { display: flex; flex-direction: column; gap: 0.35rem; margin: 0.25rem 0 0.5rem; font-size: 0.85rem;
             color: hsl(var(--twc-base-content-muted)); }
  .legenda > span { display: flex; align-items: center; gap: 0.6rem; }
  .legenda svg { flex: none; }
  .tracejado { stroke: hsl(var(--twc-base-content-muted)); stroke-width: 1.3; stroke-dasharray: 4 3; }
  .faixa { fill: hsl(var(--twc-accent) / 0.25); }

  .tabela-diferencial { overflow-x: auto; }
  .tabela-diferencial table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  .tabela-diferencial th { text-align: left; font-weight: 650; padding: 0.4rem 0.5rem;
                          border-bottom: 1px solid hsl(var(--twc-base-content) / 0.3); color: hsl(var(--twc-base-heading)); }
  .tabela-diferencial td { padding: 0.45rem 0.5rem; border-bottom: 1px solid hsl(var(--twc-base-content) / 0.1); vertical-align: top; }
  .tabela-diferencial .num { text-align: right; font-variant-numeric: tabular-nums; }
  .acima-celular { display: none; font-size: 0.78rem; color: hsl(var(--twc-base-content-muted)); }
  .ver { white-space: nowrap; padding: 0.3rem 0.6rem; border-radius: 5px; font-size: 0.8rem; font-weight: 600;
         border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .nota { font-size: 0.8rem; color: hsl(var(--twc-base-content-muted)); }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .vazio { color: hsl(var(--twc-base-content-muted)); }

  @media (max-width: 639px) {
    .passo { display: none; }
    .voltar { margin-left: 0; width: 100%; }
    .detalhar select { flex-basis: 100%; }
    /* na lista de diferencial, o eixo (ou item) vai para baixo do nome e a coluna dele some */
    .tabela-diferencial .opcional { display: none; }
    .acima-celular { display: block; }
    .tabela-diferencial td, .tabela-diferencial th { padding: 0.45rem 0.3rem; }
  }
</style>
