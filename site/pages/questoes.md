---
title: Banco de questões
description: Todas as questões objetivas desde 2016, com filtros, classificação e links para a prova e o gabarito comentado.
sidebar_position: 8
---

<script>
  import { AREAS, gravarInputs, criarCascata, linhasDe, naOrdem, paraInput, unicas } from '$lib/filtros.js';

  const conteudo = criarCascata([
    { nome: 'areas', valor: 'area', ordenar: naOrdem(AREAS) },
    { nome: 'disciplinas', valor: 'disciplina' },
    { nome: 'eixos', valor: 'id_eixo', rotulo: 'eixo' },
    { nome: 'itens', valor: 'id_item', rotulo: 'item' }
  ]);
  const naOrdemDaConsulta = () => 0;
  const IDIOMAS = [
    { valor: 'Espanhol', rotulo: 'Espanhol' },
    { valor: 'Francês', rotulo: 'Francês' },
    { valor: 'Inglês', rotulo: 'Inglês' }
  ];

  $: hier = linhasDe(hierarquia);
  $: opcAnos = unicas(linhasDe(anos), 'ano', 'rotulo_ano', naOrdemDaConsulta);
  $: opcEtapas = unicas(linhasDe(etapas), 'etapa', 'etapa', naOrdemDaConsulta);
  // A versão em idioma só existe no bloco de língua estrangeira: as opções de idioma aparecem quando essa disciplina
  // está marcada.
  const versoesPara = (disciplinas) => [
    { valor: 'Comum', rotulo: 'Comum (fora do bloco de língua estrangeira)' },
    ...((disciplinas ?? []).includes('Língua Estrangeira') ? IDIOMAS : [])
  ];

  let sel = null;
  function limparFiltros() {
    const c = conteudo.inicial(hier);
    sel = { anos: opcAnos.map((o) => o.valor), etapas: opcEtapas.map((o) => o.valor), ...c, versoes: versoesPara(c.disciplinas).map((o) => o.valor) };
  }
  $: if (!sel && hier.length && opcAnos.length && opcEtapas.length) limparFiltros();
  $: opc = sel ? conteudo.opcoes(hier, sel) : {};
  $: opcVersoes = versoesPara(sel?.disciplinas);
  function escolher(nome, valores) {
    if (['anos', 'etapas', 'versoes'].includes(nome)) sel = { ...sel, [nome]: valores };
    else {
      const novo = conteudo.escolher(hier, sel, nome, valores);
      sel = { ...novo, versoes: versoesPara(novo.disciplinas).map((o) => o.valor) };
    }
  }
  $: if (sel)
    gravarInputs(inputs_store, {
      anos: paraInput(sel.anos, opcAnos),
      etapas: paraInput(sel.etapas, opcEtapas),
      areas: paraInput(sel.areas, opc.areas),
      disciplinas: paraInput(sel.disciplinas, opc.disciplinas),
      eixos: paraInput(sel.eixos, opc.eixos),
      itens: paraInput(sel.itens, opc.itens),
      versoes: paraInput(sel.versoes, opcVersoes)
    });
</script>

Todas as questões objetivas de 2016 a 2027 com a classificação do gabarito comentado oficial. Use os filtros e a busca
(que procura em todas as colunas) e abra a prova ou o gabarito comentado direto na página da questão.

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
  <div class="linha">
    <Filtro titulo="Vestibular" opcoes={opcAnos} selecionados={sel?.anos ?? []} on:change={(e) => escolher('anos', e.detail)} />
    <Filtro titulo="Exame" opcoes={opcEtapas} selecionados={sel?.etapas ?? []} on:change={(e) => escolher('etapas', e.detail)} />
  </div>
  <div class="linha">
    <Filtro titulo="Área" opcoes={opc.areas ?? []} selecionados={sel?.areas ?? []} on:change={(e) => escolher('areas', e.detail)} />
    <span class="passo" aria-hidden="true">›</span>
    <Filtro titulo="Disciplina" opcoes={opc.disciplinas ?? []} selecionados={sel?.disciplinas ?? []} on:change={(e) => escolher('disciplinas', e.detail)} />
    <span class="passo" aria-hidden="true">›</span>
    <Filtro titulo="Eixo" opcoes={opc.eixos ?? []} selecionados={sel?.eixos ?? []} on:change={(e) => escolher('eixos', e.detail)} />
    <span class="passo" aria-hidden="true">›</span>
    <Filtro titulo="Item" opcoes={opc.itens ?? []} selecionados={sel?.itens ?? []} on:change={(e) => escolher('itens', e.detail)} />
  </div>
  <div class="linha">
    <Filtro titulo="Versão" opcoes={opcVersoes} selecionados={sel?.versoes ?? []} on:change={(e) => escolher('versoes', e.detail)} />
    <button class="limpar" on:click={limparFiltros}>Limpar filtros</button>
  </div>
</div>

```sql lista
select
    id_questao,
    exame,
    numero,
    versao,
    area,
    disciplina,
    classificacao,
    eixos,
    resposta,
    percentual_acertos / 100 as acertos,
    nivel || case when nivel_estimado then ' (estimado)' else '' end as nivel,
    observacoes,
    url_prova,
    url_comentario
from uerj.questoes
where id_exame in (select id_exame from uerj.exames where ano in ${inputs.anos.value} and etapa in ${inputs.etapas.value})
    and id_questao in (
        select id_questao
        from uerj.classificacoes
        where area in ${inputs.areas.value}
            and disciplina in ${inputs.disciplinas.value}
            and id_eixo in ${inputs.eixos.value}
            and id_item in ${inputs.itens.value}
    )
    and versao in ${inputs.versoes.value}
order by id_exame desc, numero, idioma nulls first
```

<p class="contagem">{lista.length} versões de questão na seleção.</p>

<DataTable data={lista} rows=25 search=true downloadable=true emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=disciplina title="Disciplina" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=resposta title="Gabarito" />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=observacoes title="Adendo do projeto" wrap=true />
  <Column id=url_prova title="Prova" contentType=link linkLabel="PDF ↗" openInNewTab=true />
  <Column id=url_comentario title="Gabarito comentado" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

- **Questão**: `AAAA-N-NN`, o ano do vestibular, o número do exame (o Exame Único usa 1) e o número da questão. No
  bloco de língua estrangeira, o sufixo indica o idioma (`-ES`, `-FR`, `-EN`).
- **Acertos**: percentual publicado pela UERJ. Fica vazio quando o gabarito comentado não o traz (2021, 2024-2,
  2027-2, anuladas e algumas questões de 2020-2 e 2022-1).
- **Adendo do projeto**: aparece quando o projeto completou, deduziu ou estimou parte da classificação. Todo o resto
  vem do PDF oficial.
- **Prova** abre o caderno de prova oficial na página em que a questão começa (a questão pode depender de um texto
  de páginas anteriores). **Gabarito comentado** abre a resolução oficial, com a classificação da questão.

<style>
  .painel-filtros { display: flex; flex-direction: column; gap: 0.2rem; margin: 0.5rem 0 1.25rem; padding: 0.75rem 0 0.9rem;
                    border-top: 2px solid hsl(var(--twc-base-heading)); border-bottom: 1px solid hsl(var(--twc-base-content) / 0.15); }
  .linha { display: flex; flex-wrap: wrap; align-items: center; gap: 0 0.4rem; }
  .passo { color: hsl(var(--twc-primary)); font-size: 1.2rem; }
  .limpar { margin-left: 0.5rem; padding: 0.35rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
            border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)); background: transparent; }
  .limpar:hover { background: hsl(var(--twc-primary) / 0.08); }
  .contagem { font-size: 0.85rem; color: hsl(var(--twc-base-content-muted)); }
</style>
