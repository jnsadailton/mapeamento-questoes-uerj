---
title: Histórico por conteúdo
description: A série histórica de cada eixo, item e subitem do programa, de 2016 a 2027, por disciplina e idioma.
sidebar_position: 5
---

<script>
  import { linhasDe } from '$lib/filtros.js';

  const AREAS = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];
  const IDIOMAS = { Espanhol: 'ES', Francês: 'FR', Inglês: 'EN' };
  const LE = 'Língua Estrangeira';
  const TODAS = 'Todas';
  const ehLE = (r) => r === LE || r in IDIOMAS;

  // Área › Disciplina › Eixo › Item, escolha única. As listas saem da hierarquia inteira, carregada uma vez: a
  // disciplina só oferece as da área, o eixo só os eixos com itens da disciplina e o item só os itens do eixo. Trocar
  // a área volta para "todas as disciplinas", o primeiro eixo e o item mais cobrado dele; trocar o eixo leva ao item
  // mais cobrado dele; trocar a disciplina mantém o eixo e o item quando eles existem nela.
  //
  // Disciplina: em Ciências da Natureza, cada item é de Biologia, Física ou Química (os eixos são interdisciplinares).
  // Em Linguagens, o edital usa os mesmos eixos para Língua Portuguesa, Literatura e Língua Estrangeira: Língua
  // Portuguesa e Literatura são as questões em português (pelo item), e Língua Estrangeira é o bloco de espanhol,
  // francês e inglês, visto inteiro ou um idioma por vez.
  let area = 'Matemática';
  let recorte = TODAS;
  let eixo = null;
  let item = null;

  $: hier = linhasDe(conteudos);
  $: listaExames = linhasDe(exames_mapa);

  // Questões de cada recorte|conteúdo|exame e o total de cada recorte|conteúdo desde 2016.
  $: porExame = new Map(linhasDe(contagens).map((r) => [r.recorte + '|' + r.id_conteudo + '|' + r.id_exame, Number(r.questoes)]));
  $: totais = somar(linhasDe(contagens), listaExames);
  function somar(linhas, exames) {
    const ano = new Map(exames.map((e) => [e.id_exame, Number(e.ano)]));
    const t = new Map();
    for (const r of linhas) {
      const chave = r.recorte + '|' + r.id_conteudo;
      if (!t.has(chave)) t.set(chave, { questoes: 0, exames: 0, ultimo_ano: 0 });
      const s = t.get(chave);
      s.questoes += Number(r.questoes);
      s.exames += 1;
      s.ultimo_ano = Math.max(s.ultimo_ano, ano.get(r.id_exame) ?? 0);
    }
    return t;
  }
  const totalDe = (t, r, id) => t.get(r + '|' + id)?.questoes ?? 0;

  $: areas = AREAS.filter((a) => hier.some((r) => r.area === a));
  $: grupos = recortesDe(hier, area);
  $: eixos = eixosDe(hier, area, recorte);
  $: itens = itensDe(hier, area, recorte, eixo, totais);

  // As opções do passo 2, em grupos (o de língua estrangeira vira um <optgroup>). Área de uma disciplina só: uma
  // opção, com o nome dela.
  function recortesDe(linhas, a) {
    const disciplinas = [...new Set(linhas.filter((r) => r.area === a).map((r) => r.disciplina))].sort((x, y) => x.localeCompare(y, 'pt'));
    if (disciplinas.length < 2) return [{ grupo: null, opcoes: [{ valor: TODAS, rotulo: disciplinas[0] ?? a }] }];
    const lista = [{ grupo: null, opcoes: [{ valor: TODAS, rotulo: 'Todas as disciplinas' }, ...disciplinas.map((d) => ({ valor: d, rotulo: d }))] }];
    if (a === 'Linguagens')
      lista.push({
        grupo: LE,
        opcoes: [{ valor: LE, rotulo: 'Os três idiomas' }, ...Object.keys(IDIOMAS).map((i) => ({ valor: i, rotulo: i }))]
      });
    return lista;
  }
  // O conteúdo entra no recorte? (língua estrangeira usa o programa inteiro de Linguagens)
  const noRecorte = (r, linha) => r === TODAS || (ehLE(r) ? linha.area === 'Linguagens' : linha.disciplina === r);

  function eixosDe(linhas, a, r) {
    const vistos = new Map();
    for (const l of linhas)
      if (l.nivel === 'item' && l.area === a && noRecorte(r, l) && !vistos.has(l.id_eixo)) vistos.set(l.id_eixo, l.eixo);
    return [...vistos].map(([id, nome]) => ({ id, nome })).sort((x, y) => x.id.localeCompare(y.id));
  }
  function itensDe(linhas, a, r, e, t) {
    return linhas
      .filter((l) => l.nivel === 'item' && l.area === a && l.id_eixo === e && noRecorte(r, l))
      .map((l) => ({ id: l.id_item, nome: l.item, vigente: l.vigente, questoes: totalDe(t, r, l.id_item) }))
      .sort((x, y) => y.questoes - x.questoes || x.nome.localeCompare(y.nome));
  }
  function escolherArea(a) {
    area = a;
    recorte = TODAS;
    escolherEixo(eixosDe(hier, a, TODAS)[0]?.id ?? null);
  }
  function escolherRecorte(r) {
    recorte = r;
    const novosEixos = eixosDe(hier, area, r);
    if (!novosEixos.some((e) => e.id === eixo)) return escolherEixo(novosEixos[0]?.id ?? null);
    const novosItens = itensDe(hier, area, r, eixo, totais);
    if (!novosItens.some((i) => i.id === item)) item = novosItens[0]?.id ?? null;
  }
  function escolherEixo(e) {
    eixo = e;
    item = itensDe(hier, area, recorte, e, totais)[0]?.id ?? null;
  }
  $: if (hier.length && totais.size && eixo === null) escolherArea(area);

  $: nomeEixo = eixos.find((e) => e.id === eixo)?.nome ?? '';
  $: nomeItem = itens.find((i) => i.id === item)?.nome ?? '';
  $: emRecorte = recorte === TODAS ? '' : ', em ' + (recorte === LE ? 'Língua Estrangeira (os três idiomas)' : recorte);

  // Uma linha por conteúdo × exame (vazia quando o conteúdo não caiu no exame), no recorte escolhido.
  function linhasDoMapa(lista, campo, idCampo, exames, r, contagem, t) {
    return lista.flatMap((c) => {
      const nome = c.nome + (c.vigente ? '' : ' *') + (totalDe(t, r, c.id) === 0 ? ' (nunca caiu)' : '');
      return exames.map((e) => ({
        exame: e.rotulo,
        id_exame: e.id_exame,
        [campo]: nome,
        [idCampo]: c.id,
        questoes: contagem.get(r + '|' + c.id + '|' + e.id_exame) ?? null
      }));
    });
  }
  $: subitens = hier
    .filter((l) => l.nivel === 'subitem' && l.id_item === item)
    .map((l) => ({ id: l.id_subitem, nome: l.subitem, vigente: l.vigente }));
  $: dadosItens = linhasDoMapa(itens, 'item', 'id_item', listaExames, recorte, porExame, totais);
  $: dadosSubitens = linhasDoMapa(subitens, 'subitem', 'id_subitem', listaExames, recorte, porExame, totais);
  $: totalItem = totais.get(recorte + '|' + item);
  $: resumo = totalItem ? [totalItem] : [];
  // A versão da questão entra no recorte? (disciplina da classificação, ou o idioma da versão)
  const naVersao = (r, q) => r === TODAS || (r in IDIOMAS ? q.idioma === IDIOMAS[r] : q.disciplina === r);
  $: dadosQuestoes = linhasDe(questoes_itens).filter((q) => q.id_item === item && naVersao(recorte, q));

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
  // (a altura do gráfico inclui a faixa das datas, que o ECharts desconta antes de desenhar as linhas)
  const opcoesMapa = { yAxis: { axisLabel: { interval: 0, lineHeight: 13, formatter: (v) => rotuloCurto(v) } } };
  $: nItens = itens.length;
  $: nSubitens = subitens.length;
</script>

Escolha um conteúdo e veja em que exames ele caiu desde 2016. Cada célula dos mapas é o número de questões daquele
exame (vazia quando nenhuma).

<Hierarquia compacto=true />

```sql exames_mapa
select id_exame, rotulo, ano from uerj.exames order by id_exame
```

```sql conteudos
select nivel, area, disciplina, id_eixo, eixo, id_item, item, id_subitem, subitem, vigente from uerj.conteudo
```

```sql contagens
-- Questões por exame, recorte e conteúdo (item ou subitem). Recortes: a disciplina da classificação (Física,
-- Língua Portuguesa, Língua Estrangeira...), cada idioma do bloco de língua estrangeira e "Todas". A unidade é o
-- número da questão: as versões de língua estrangeira de um mesmo número contam uma vez.
with base as (
    select id_exame, numero, disciplina as recorte, id_item, id_subitem from uerj.classificacoes
    union all
    select
        id_exame,
        numero,
        case idioma when 'ES' then 'Espanhol' when 'FR' then 'Francês' when 'EN' then 'Inglês' end,
        id_item,
        id_subitem
    from uerj.classificacoes
    where idioma is not null
    union all
    select id_exame, numero, 'Todas', id_item, id_subitem from uerj.classificacoes
)
select id_exame, recorte, id_item as id_conteudo, cast(count(distinct numero) as integer) as questoes
from base
group by all
union all
select id_exame, recorte, id_subitem, cast(count(distinct numero) as integer)
from base
where id_subitem is not null
group by all
```

```sql questoes_itens
select
    c.id_item,
    c.disciplina,
    q.idioma,
    q.id_questao,
    q.classificacao,
    q.resposta,
    q.percentual_acertos / 100 as acertos,
    q.observacoes,
    q.url_prova,
    q.url_comentario
from (select distinct id_item, disciplina, id_questao from uerj.classificacoes) as c
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
      <span class="rotulo">Disciplina <small>da área escolhida</small></span>
      <select value={recorte} on:change={(e) => escolherRecorte(e.currentTarget.value)} disabled={grupos.length === 1 && grupos[0].opcoes.length === 1}>
        {#each grupos as g}
          {#if g.grupo}
            <optgroup label={g.grupo}>
              {#each g.opcoes as o}<option value={o.valor}>{o.rotulo}</option>{/each}
            </optgroup>
          {:else}
            {#each g.opcoes as o}<option value={o.valor}>{o.rotulo}</option>{/each}
          {/if}
        {/each}
      </select>
    </label>
    <span class="seta" aria-hidden="true">›</span>
    <label class="passo">
      <span class="num">3</span>
      <span class="rotulo">Eixo <small>da disciplina escolhida</small></span>
      <select value={eixo} on:change={(e) => escolherEixo(e.currentTarget.value)} disabled={!eixos.length}>
        {#each eixos as e}<option value={e.id}>{e.nome}</option>{/each}
      </select>
    </label>
    <span class="seta" aria-hidden="true">›</span>
    <label class="passo">
      <span class="num">4</span>
      <span class="rotulo">Item <small>do eixo escolhido (questões desde 2016)</small></span>
      <select bind:value={item} disabled={!itens.length}>
        {#each itens as i}<option value={i.id}>{i.nome} ({i.questoes})</option>{/each}
      </select>
    </label>
  </div>
  <p class="escolha-nota">Ao trocar a área, a disciplina, o eixo e o item mudam sozinhos para os da nova área; ao trocar
  o eixo, o item muda para o mais cobrado dele.</p>
  {#if area === 'Linguagens'}
    <p class="escolha-nota">Em Linguagens, o edital usa os mesmos eixos para as três disciplinas. Língua Portuguesa e
    Literatura contam só as questões em português. Língua Estrangeira conta o bloco de espanhol, francês e inglês: as
    três versões de uma questão contam uma vez, e escolher um idioma mostra só as questões dele.</p>
  {:else if area === 'Ciências da Natureza'}
    <p class="escolha-nota">Os eixos de Ciências da Natureza misturam as disciplinas: com Biologia, Física ou Química
    escolhida, cada eixo mostra só os itens dela.</p>
  {/if}
</div>

## Itens do eixo {nomeEixo}{emRecorte}, exame a exame

<div class="mapa-rolagem"><div class="mapa-largo">
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
</div></div>
<p class="dica-rolagem">Arraste o mapa para o lado para ver todos os exames.</p>

Itens marcados com * não estão mais no edital de 2027; eles aparecem porque caíram em exames anteriores. "Nunca
caiu" quer dizer que nenhum gabarito comentado oficial classificou uma questão nesse conteúdo desde 2016 (na disciplina
escolhida), mesmo ele estando no edital: uma questão pode usar a ideia (conjuntos numa questão de probabilidade, por exemplo) e ser
classificada pela UERJ em outro item.

## O item {nomeItem}{emRecorte}, subitem por subitem

<Grid cols=3>
  <BigValue data={resumo} value=questoes title="Questões desde 2016" emptySet=pass emptyMessage="0" valueClass="valor" />
  <BigValue data={resumo} value=exames title="Exames em que caiu (de 21)" emptySet=pass emptyMessage="0" valueClass="valor" />
  <BigValue data={resumo} value=ultimo_ano fmt="0" title="Último vestibular em que caiu" emptySet=pass emptyMessage="nunca caiu" valueClass="valor" />
</Grid>

<div class="mapa-rolagem"><div class="mapa-largo">
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
</div></div>
<p class="dica-rolagem">Arraste o mapa para o lado para ver todos os exames.</p>

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
  .mapa-rolagem { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .dica-rolagem { display: none; margin: 0.25rem 0 0; font-size: 0.8rem; color: hsl(var(--twc-base-content-muted)); }
  @media (max-width: 640px) {
    .seta { display: none; }
    select { max-width: 100%; width: 100%; }
    .passo { width: 100%; }
    .mapa-largo { min-width: 760px; }
    .dica-rolagem { display: block; }
  }
</style>
