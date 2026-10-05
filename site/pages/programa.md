---
title: Programa
description: "O dicionário do programa da UERJ: todas as áreas, eixos, itens e subitens, com o que já caiu de cada um."
sidebar_position: 2
---

<script>
  const AREAS = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];
  const COR = {
    'Linguagens': 'var(--twc-area-lin)',
    'Matemática': 'var(--twc-area-mat)',
    'Ciências da Natureza': 'var(--twc-area-cnt)',
    'Ciências Humanas': 'var(--twc-area-chs)'
  };

  // Ciências da Natureza: cada item é de uma disciplina (os eixos são interdisciplinares).
  const CNT = 'Ciências da Natureza';
  const DISCIPLINAS_CNT = ['Biologia', 'Física', 'Química'];

  let busca = '';
  let areasSel = new Set(); // vazio = todas
  let disciplinasSel = new Set(); // vazio = todas (só vale para Ciências da Natureza)
  let incluirAntigos = false;

  const normalizar = (t) => (t ?? '').toString().normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const plural = (n, um, varios) => n + ' ' + (n === 1 ? um : varios);

  function alternarArea(a) {
    const s = new Set(areasSel);
    s.has(a) ? s.delete(a) : s.add(a);
    areasSel = s;
  }
  function alternarDisciplina(d) {
    const s = new Set(disciplinasSel);
    s.has(d) ? s.delete(d) : s.add(d);
    disciplinasSel = s;
  }

  // Área › Eixo › Item › Subitem a partir das linhas (uma por subitem), mantendo a ordem dos IDs.
  function montar(linhas) {
    const areas = new Map();
    for (const l of linhas) {
      if (!areas.has(l.area)) areas.set(l.area, { nome: l.area, eixos: new Map() });
      const eixos = areas.get(l.area).eixos;
      if (!eixos.has(l.id_eixo)) eixos.set(l.id_eixo, { id: l.id_eixo, nome: l.eixo, itens: new Map() });
      const itens = eixos.get(l.id_eixo).itens;
      if (!itens.has(l.id_item))
        itens.set(l.id_item, {
          id: l.id_item, nome: l.item, disciplina: l.disciplina, vigente: l.item_vigente, questoes: Number(l.questoes_item),
          subitens: []
        });
      itens.get(l.id_item).subitens.push(l);
    }
    return AREAS.filter((a) => areas.has(a)).map((a) => {
      const area = areas.get(a);
      const eixos = [...area.eixos.values()].map((e) => ({ ...e, itens: [...e.itens.values()] }));
      const itens = eixos.flatMap((e) => e.itens);
      return { nome: a, eixos, qtdItens: itens.length, qtdSubitens: itens.reduce((n, i) => n + i.subitens.length, 0) };
    });
  }

  $: linhas = programa && programa.length ? Array.from(programa) : [];
  $: termo = normalizar(busca.trim());
  $: filtradas = linhas.filter(
    (l) =>
      (incluirAntigos || l.subitem_vigente) &&
      (areasSel.size === 0 || areasSel.has(l.area)) &&
      (disciplinasSel.size === 0 || l.area !== CNT || disciplinasSel.has(l.disciplina)) &&
      (!termo || normalizar([l.area, l.eixo, l.item, l.subitem, l.outras_redacoes].join(' ')).includes(termo))
  );
  $: arvore = montar(filtradas);
  $: buscando = termo.length > 0;
  $: mostraDisciplinas = areasSel.size === 0 || areasSel.has(CNT);
</script>

O programa da UERJ organiza tudo o que pode cair em quatro níveis. Esta página mostra a lista completa, como um
dicionário: abra uma área, um eixo e um item para ver os subitens e quanto cada um já caiu desde o Vestibular 2016.

<AnoVestibular />

<Hierarquia />

```sql programa
select * from uerj.programa order by id_subitem
```

<div class="controles">
  <label class="busca">
    <span>Buscar no programa</span>
    <input type="search" bind:value={busca} placeholder="Ex.: porcentagem, genética, Revolução Francesa" />
  </label>
  <div class="chips" role="group" aria-label="Filtrar por área">
    {#each AREAS as a}
      <button
        class="chip"
        class:ativo={areasSel.has(a)}
        aria-pressed={areasSel.has(a)}
        style={'--cor: ' + COR[a]}
        on:click={() => alternarArea(a)}>{a}</button>
    {/each}
  </div>
  {#if mostraDisciplinas}
    <div class="chips" role="group" aria-label="Filtrar Ciências da Natureza por disciplina">
      <span class="chips-rotulo">Ciências da Natureza:</span>
      {#each DISCIPLINAS_CNT as d}
        <button
          class="chip"
          class:ativo={disciplinasSel.has(d)}
          aria-pressed={disciplinasSel.has(d)}
          style={'--cor: ' + COR[CNT]}
          on:click={() => alternarDisciplina(d)}>{d}</button>
      {/each}
    </div>
  {/if}
  <label class="antigos">
    <input type="checkbox" bind:checked={incluirAntigos} />
    Incluir conteúdos que saíram do edital (aparecem em editais antigos)
  </label>
</div>

<p class="resumo">
  {#if !linhas.length}
    Carregando o programa…
  {:else if !filtradas.length}
    Nada encontrado{busca ? ' para "' + busca + '"' : ''}. Tente outra palavra ou limpe os filtros de área.
  {:else}
    {plural(filtradas.length, 'subitem', 'subitens')}{busca ? ' com "' + busca + '"' : ''}{areasSel.size ? ' em ' + [...areasSel].join(', ') : ''}{mostraDisciplinas && disciplinasSel.size ? ' (Ciências da Natureza: ' + [...disciplinasSel].join(', ') + ')' : ''}.
    {#if buscando}A busca também procura nas outras redações dos editais antigos.{/if}
  {/if}
</p>

<div class="arvore">
  {#each arvore as area (area.nome)}
    <details class="area" open style={'--cor: ' + COR[area.nome]}>
      <summary>
        <span class="nome">{area.nome}</span>
        <span class="conta">{plural(area.eixos.length, 'eixo', 'eixos')}, {plural(area.qtdItens, 'item', 'itens')} e {plural(area.qtdSubitens, 'subitem', 'subitens')}</span>
      </summary>
      {#if area.nome === 'Linguagens'}
        <p class="nota-area">O edital tem um programa só para as três disciplinas de Linguagens: Língua Portuguesa,
        Literatura e Língua Estrangeira (espanhol, francês ou inglês). Por isso as contagens desta área juntam as questões
        em português e as do bloco de língua estrangeira; as três versões de uma questão de língua estrangeira contam uma
        vez. Para ver cada disciplina ou idioma separado, use o <a href="/historico">Histórico por conteúdo</a>.</p>
      {:else if area.nome === CNT}
        <p class="nota-area">Os eixos de Ciências da Natureza misturam Biologia, Física e Química; a disciplina de cada
        item aparece ao lado do nome dele.</p>
      {/if}
      {#each area.eixos as eixo (eixo.id)}
        <details class="eixo" open={buscando}>
          <summary>
            <span class="nivel">Eixo</span>
            <span class="nome">{eixo.nome}</span>
            <span class="conta">{plural(eixo.itens.length, 'item', 'itens')}</span>
          </summary>
          {#each eixo.itens as item (item.id)}
            <details class="item" open={buscando}>
              <summary>
                <span class="nivel">Item</span>
                <span class="nome">{item.nome}</span>
                {#if area.nome === CNT}<span class="disciplina">{item.disciplina}</span>{/if}
                {#if !item.vigente}<span class="tag">fora do edital de 2027</span>{/if}
                <span class="badge" class:zero={!item.questoes}>{plural(item.questoes, 'questão', 'questões')}</span>
              </summary>
              <ul>
                {#each item.subitens as s (s.id_subitem)}
                  <li>
                    <div class="linha-subitem">
                      <span class="nome">{s.subitem}</span>
                      {#if !s.subitem_vigente}<span class="tag">fora do edital de 2027</span>{/if}
                      {#if Number(s.questoes_subitem) > 0}
                        <span class="badge">{plural(Number(s.questoes_subitem), 'questão', 'questões')}</span>
                      {:else if s.subitem_vigente}
                        <span class="badge zero">nunca caiu</span>
                      {/if}
                    </div>
                    <div class="detalhes">
                      {#if s.no_edital_desde}No edital desde {s.no_edital_desde}.{/if}
                      {#if s.outras_redacoes}
                        <span class="outras">Também aparece como: {s.outras_redacoes}</span>
                      {/if}
                    </div>
                  </li>
                {/each}
              </ul>
            </details>
          {/each}
        </details>
      {/each}
    </details>
  {/each}
</div>

As redações mudam de um edital para outro ("sequências" e "sucessões", subitens que trocaram de item). O projeto liga
cada redação antiga ao conteúdo atual equivalente; é por isso que uma questão do Vestibular 2016 conta para o subitem do edital de 2027.
A contagem de questões é a mesma das outras páginas: cada número de questão conta uma vez.

<style>
  .controles { display: flex; flex-wrap: wrap; gap: 0.75rem 1.25rem; align-items: flex-end; margin: 0.5rem 0 0.75rem; }
  .busca { display: flex; flex-direction: column; gap: 0.25rem; flex: 1 1 18rem; font-size: 0.8rem; font-weight: 600;
           color: hsl(var(--twc-base-content-muted)); }
  .busca input { padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.95rem; font-weight: 400;
                 border: 1px solid hsl(var(--twc-base-content) / 0.25); background: hsl(var(--twc-base-100));
                 color: hsl(var(--twc-base-content)); }
  .busca input:focus { outline: 2px solid hsl(var(--twc-primary) / 0.6); outline-offset: 1px; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip { padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; cursor: pointer;
          border: 1px solid hsl(var(--cor) / 0.6); color: hsl(var(--twc-base-content)); background: transparent; }
  .chip.ativo { background: hsl(var(--cor)); border-color: hsl(var(--cor)); color: #0b0b0b; }
  .chips-rotulo { align-self: center; font-size: 0.8rem; font-weight: 600; color: hsl(var(--twc-base-content-muted)); }
  .nota-area { margin: 0.4rem 0 0.2rem 0.6rem; max-width: 72ch; font-size: 0.85rem; line-height: 1.5;
               color: hsl(var(--twc-base-content-muted)); }
  .nota-area a { color: hsl(var(--twc-primary)); text-decoration: underline; text-underline-offset: 2px; }
  .disciplina { font-size: 0.72rem; font-weight: 600; padding: 0.05rem 0.45rem; border-radius: 4px;
                background: hsl(var(--cor) / 0.18); color: hsl(var(--twc-base-content)); }
  .antigos { display: flex; gap: 0.4rem; align-items: center; font-size: 0.85rem; }
  .resumo { font-size: 0.9rem; color: hsl(var(--twc-base-content-muted)); }
  .arvore { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1.5rem; }
  details > summary { cursor: pointer; list-style: none; display: flex; flex-wrap: wrap; align-items: baseline;
                      gap: 0.35rem 0.6rem; }
  details > summary::-webkit-details-marker { display: none; }
  details > summary::before { content: '▸'; color: hsl(var(--twc-primary)); width: 0.8rem; flex: none;
                              transition: transform 0.15s; }
  details[open] > summary::before { transform: rotate(90deg); }
  .area { border-radius: 10px; border: 1px solid hsl(var(--twc-base-content) / 0.12);
          border-left: 5px solid hsl(var(--cor)); padding: 0.6rem 0.9rem; }
  .area > summary .nome { font-family: var(--fonte-titulo); font-size: 1.4rem; font-weight: 600; color: hsl(var(--twc-base-heading)); }
  .eixo { margin: 0.4rem 0 0 0.6rem; padding: 0.35rem 0.6rem; border-left: 2px solid hsl(var(--cor) / 0.5); }
  .eixo > summary .nome { font-weight: 700; }
  .item { margin: 0.3rem 0 0 0.8rem; }
  .item > summary .nome { font-weight: 600; }
  .nivel { font-size: 0.75rem; font-weight: 600; color: hsl(var(--twc-primary)); }
  .conta, .detalhes { font-size: 0.8rem; color: hsl(var(--twc-base-content-muted)); }
  .badge { font-size: 0.75rem; font-weight: 600; padding: 0.05rem 0.5rem; border-radius: 999px;
           background: hsl(var(--twc-primary) / 0.12); color: hsl(var(--twc-primary)); font-variant-numeric: tabular-nums; }
  .badge.zero { background: hsl(var(--twc-base-content) / 0.08); color: hsl(var(--twc-base-content-muted)); }
  .tag { font-size: 0.7rem; padding: 0.05rem 0.45rem; border-radius: 4px;
         border: 1px solid hsl(var(--twc-accent) / 0.7); color: hsl(var(--twc-base-content)); }
  ul { margin: 0.3rem 0 0.5rem 1.6rem; padding: 0; list-style: none; }
  li { padding: 0.35rem 0; border-bottom: 1px solid hsl(var(--twc-base-content) / 0.07); }
  .linha-subitem { display: flex; flex-wrap: wrap; gap: 0.3rem 0.6rem; align-items: baseline; }
  .outras { font-style: italic; }
</style>
