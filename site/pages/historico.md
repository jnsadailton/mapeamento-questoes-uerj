---
title: Histórico por conteúdo
description: A série histórica de cada eixo, item e subitem do programa, de 2016 a 2027.
sidebar_position: 5
---

<script>
  import { linhasDe } from '$lib/filtros.js';

  const AREAS = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];

  // Área › Eixo › Item, escolha única. As listas saem da hierarquia inteira, carregada uma vez: o eixo só oferece os
  // eixos da área escolhida e o item só os itens do eixo. Trocar a área leva ao primeiro eixo dela e ao item mais
  // cobrado desse eixo; trocar o eixo leva ao item mais cobrado dele.
  let area = 'Matemática';
  let eixo = null;
  let item = null;

  $: hier = linhasDe(hierarquia);
  $: areas = AREAS.filter((a) => hier.some((r) => r.area === a));
  $: eixos = eixosDe(hier, area);
  $: itens = itensDe(hier, eixo);

  function eixosDe(linhas, a) {
    const vistos = new Map();
    for (const r of linhas) if (r.area === a && !vistos.has(r.id_eixo)) vistos.set(r.id_eixo, r.eixo);
    return [...vistos].map(([id, nome]) => ({ id, nome })).sort((x, y) => x.id.localeCompare(y.id));
  }
  function itensDe(linhas, e) {
    return linhas
      .filter((r) => r.id_eixo === e)
      .map((r) => ({ id: r.id_item, nome: r.item, questoes: Number(r.questoes) }))
      .sort((x, y) => y.questoes - x.questoes || x.nome.localeCompare(y.nome));
  }
  function escolherArea(a) {
    area = a;
    escolherEixo(eixosDe(hier, a)[0]?.id ?? null);
  }
  function escolherEixo(e) {
    eixo = e;
    item = itensDe(hier, e)[0]?.id ?? null;
  }
  $: if (hier.length && eixo === null) escolherArea(area);

  $: nomeEixo = eixos.find((e) => e.id === eixo)?.nome ?? '';
  $: nomeItem = itens.find((i) => i.id === item)?.nome ?? '';
  $: dadosItens = linhasDe(mapa_itens).filter((r) => r.id_eixo === eixo);
  $: dadosSubitens = linhasDe(mapa_subitens).filter((r) => r.id_item === item);
  $: dadosQuestoes = linhasDe(questoes_itens).filter((r) => r.id_item === item);
  $: resumo = linhasDe(resumo_itens).filter((r) => r.id_item === item);

  // Nomes longos de conteúdo empurravam o mapa para a direita: o rótulo quebra em até duas linhas de ~34 caracteres,
  // com reticências se passar disso (o nome inteiro aparece ao passar o mouse). Todos os rótulos ficam visíveis.
  function rotuloCurto(texto, largura = 34) {
    const linhas = [''];
    for (const palavra of String(texto).split(' ')) {
      const atual = linhas[linhas.length - 1];
      if (!atual || (atual + ' ' + palavra).length <= largura) linhas[linhas.length - 1] = atual ? atual + ' ' + palavra : palavra;
      else linhas.push(palavra);
    }
    // quebra de linha sem barra invertida: o pré-processador de Markdown do Evidence estraga a barra dentro do script
    const quebra = String.fromCharCode(10);
    if (linhas.length <= 2) return linhas.join(quebra);
    const segunda = linhas[1].length > largura - 1 ? linhas[1].slice(0, largura - 1) : linhas[1];
    return linhas[0] + quebra + segunda + '…';
  }
  // Altura: 34 px por linha mais o espaço das datas inclinadas no topo (sem isso, mapas com poucas linhas ficavam
  // espremidos e os rótulos se sobrepunham).
  const LINHA = 34;
  const DATAS = 72;
  const linhasDoMapa = (dados, campo) => new Set(dados.map((r) => r[campo])).size;
  // (a altura do gráfico inclui a faixa das datas, que o ECharts desconta antes de desenhar as linhas)
  const opcoesMapa = { yAxis: { axisLabel: { interval: 0, lineHeight: 13, formatter: (v) => rotuloCurto(v) } } };
  $: nItens = linhasDoMapa(dadosItens, 'item');
  $: nSubitens = linhasDoMapa(dadosSubitens, 'subitem');
</script>

Escolha um conteúdo e veja em que exames ele caiu desde 2016. Cada célula dos mapas é o número de questões daquele
exame (vazia quando nenhuma).

<Hierarquia compacto=true />

```sql hierarquia
select c.area, c.id_eixo, c.eixo, c.id_item, c.item, coalesce(r.qtd_questoes, 0) as questoes
from uerj.conteudo as c
left join uerj.recorrencia as r on r.nivel = 'item' and r.id_conteudo = c.id_item
where c.nivel = 'item'
```

```sql mapa_itens
select
    e.rotulo as exame,
    e.id_exame,
    c.id_eixo,
    c.item || case when c.vigente then '' else ' *' end
        || case when sum(coalesce(i.qtd_questoes, 0)) over (partition by c.id_item) = 0 then ' (nunca caiu)' else '' end
        as item,
    c.id_item,
    i.qtd_questoes as questoes
from uerj.exames as e
cross join (select id_eixo, id_item, item, vigente from uerj.conteudo where nivel = 'item') as c
left join uerj.incidencia as i
    on i.id_exame = e.id_exame and i.nivel = 'item' and i.id_conteudo = c.id_item
```

```sql mapa_subitens
select
    e.rotulo as exame,
    e.id_exame,
    c.id_item,
    c.subitem || case when c.vigente then '' else ' *' end
        || case when sum(coalesce(i.qtd_questoes, 0)) over (partition by c.id_subitem) = 0 then ' (nunca caiu)' else '' end
        as subitem,
    c.id_subitem,
    i.qtd_questoes as questoes
from uerj.exames as e
cross join (select id_item, id_subitem, subitem, vigente from uerj.conteudo where nivel = 'subitem') as c
left join uerj.incidencia as i
    on i.id_exame = e.id_exame and i.nivel = 'subitem' and i.id_conteudo = c.id_subitem
```

```sql resumo_itens
select
    id_conteudo as id_item,
    cast(sum(qtd_questoes) as integer) as questoes,
    count(distinct id_exame) as exames,
    max(ano) as ultimo_ano
from uerj.incidencia
where nivel = 'item'
group by all
```

```sql questoes_itens
select
    c.id_item,
    q.id_questao,
    q.classificacao,
    q.resposta,
    q.percentual_acertos / 100 as acertos,
    q.observacoes,
    q.url_prova,
    q.url_comentario
from (select distinct id_item, id_questao from uerj.classificacoes) as c
inner join uerj.questoes as q using (id_questao)
order by q.id_questao desc
```

<div class="escolha">
  <p class="escolha-titulo">Escolha nesta ordem</p>
  <div class="passos">
    <label class="passo">
      <span class="num">1</span>
      <span class="rotulo">Área</span>
      <select value={area} on:change={(e) => escolherArea(e.currentTarget.value)}>
        {#each areas as a}<option value={a}>{a}</option>{/each}
      </select>
    </label>
    <span class="seta" aria-hidden="true">›</span>
    <label class="passo">
      <span class="num">2</span>
      <span class="rotulo">Eixo <small>da área escolhida</small></span>
      <select value={eixo} on:change={(e) => escolherEixo(e.currentTarget.value)} disabled={!eixos.length}>
        {#each eixos as e}<option value={e.id}>{e.nome}</option>{/each}
      </select>
    </label>
    <span class="seta" aria-hidden="true">›</span>
    <label class="passo">
      <span class="num">3</span>
      <span class="rotulo">Item <small>do eixo escolhido (questões desde 2016)</small></span>
      <select bind:value={item} disabled={!itens.length}>
        {#each itens as i}<option value={i.id}>{i.nome} ({i.questoes})</option>{/each}
      </select>
    </label>
  </div>
  <p class="escolha-nota">Ao trocar a área, o eixo e o item mudam sozinhos para os da nova área; ao trocar o eixo, o item
  muda para o mais cobrado dele.</p>
</div>

## Itens do eixo {nomeEixo}, exame a exame

<Heatmap
  data={dadosItens}
  x=exame
  xSort=id_exame
  y=item
  ySort=id_item
  value=questoes
  xLabelRotation=-45
  legend=false
  chartAreaHeight={nItens * LINHA + DATAS}
  echartsOptions={opcoesMapa}
  nullsZero=false
  min=0
  rightPadding=40
  emptySet=pass
  emptyMessage="Nenhum conteúdo para mostrar."
/>

Itens marcados com * não estão mais no edital de 2027; eles aparecem porque caíram em exames anteriores. "Nunca
caiu" quer dizer que nenhum gabarito comentado oficial classificou uma questão nesse conteúdo desde 2016, mesmo ele
estando no edital: uma questão pode usar a ideia (conjuntos numa questão de probabilidade, por exemplo) e ser
classificada pela UERJ em outro item.

## O item {nomeItem}, subitem por subitem

<Grid cols=3>
  <BigValue data={resumo} value=questoes title="Questões desde 2016" emptySet=pass emptyMessage="0" valueClass="valor" />
  <BigValue data={resumo} value=exames title="Exames em que caiu (de 21)" emptySet=pass emptyMessage="0" valueClass="valor" />
  <BigValue data={resumo} value=ultimo_ano fmt="0" title="Último vestibular em que caiu" emptySet=pass emptyMessage="nunca caiu" valueClass="valor" />
</Grid>

<Heatmap
  data={dadosSubitens}
  x=exame
  xSort=id_exame
  y=subitem
  ySort=id_subitem
  value=questoes
  xLabelRotation=-45
  legend=false
  chartAreaHeight={nSubitens * LINHA + DATAS}
  echartsOptions={opcoesMapa}
  nullsZero=false
  min=0
  rightPadding=40
  emptySet=pass
  emptyMessage="Nenhum conteúdo para mostrar."
/>

Quando o comentário oficial só informa o item, a questão conta para o item, mas não para nenhum subitem.

### As questões do item

<DataTable data={dadosQuestoes} rows=15 emptySet=pass emptyMessage="Nenhuma questão ligada a este item.">
  <Column id=id_questao title="Questão" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=resposta title="Gabarito" />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=observacoes title="Adendo do projeto" wrap=true />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_comentario title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

<style>
  .escolha { margin: 0.5rem 0 1.5rem; padding: 0.9rem 0 1rem; border-top: 2px solid hsl(var(--twc-base-heading));
             border-bottom: 1px solid hsl(var(--twc-base-content) / 0.15); }
  .escolha-titulo { margin: 0 0 0.6rem; font-size: 0.9rem; font-weight: 650; color: hsl(var(--twc-base-heading)); }
  .passos { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 0.5rem 0.6rem; }
  .passo { display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 0.25rem 0.45rem; min-width: 0; }
  .num { grid-row: span 2; display: inline-flex; align-items: center; justify-content: center; width: 1.75rem;
         height: 1.75rem; border-radius: 999px; font-family: var(--fonte-titulo); font-size: 1.05rem; font-weight: 600;
         background: hsl(var(--twc-primary)); color: hsl(var(--twc-primary-content)); }
  .rotulo { font-size: 0.8rem; font-weight: 600; color: hsl(var(--twc-base-heading)); }
  .rotulo small { font-weight: 400; color: hsl(var(--twc-base-content-muted)); }
  select { height: 2rem; max-width: 22rem; padding: 0 0.5rem; border-radius: 6px; font-size: 0.875rem;
           border: 1px solid hsl(var(--twc-base-content) / 0.25); background: hsl(var(--twc-base-100));
           color: hsl(var(--twc-base-content)); }
  select:focus { outline: 2px solid hsl(var(--twc-primary) / 0.6); outline-offset: 1px; }
  .seta { color: hsl(var(--twc-primary)); font-size: 1.3rem; padding-bottom: 0.2rem; }
  .escolha-nota { margin: 0.6rem 0 0; font-size: 0.8rem; color: hsl(var(--twc-base-content-muted)); }
  @media (max-width: 640px) { .seta { display: none; } select { max-width: 100%; width: 100%; } .passo { width: 100%; } }
</style>
