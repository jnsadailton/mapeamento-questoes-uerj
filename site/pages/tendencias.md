---
title: Tendências
description: O que cai em quase toda prova, o que está em alta ou em baixa e o que sumiu mas costuma voltar.
sidebar_position: 4
---

<script>
  import { AREAS, gravarInputs, criarCascata, linhasDe, naOrdem, paraInput } from '$lib/filtros.js';

  // Área › Disciplina › Eixo: cada filtro só oferece o que existe dentro do que está marcado acima.
  const conteudo = criarCascata([
    { nome: 'areas', valor: 'area', ordenar: naOrdem(AREAS) },
    { nome: 'disciplinas', valor: 'disciplina' },
    { nome: 'eixos', valor: 'eixo' }
  ]);
  $: hier = linhasDe(hierarquia);
  let sel = null;
  $: if (!sel && hier.length) sel = conteudo.inicial(hier);
  $: opc = sel ? conteudo.opcoes(hier, sel) : {};
  const escolher = (nome, valores) => (sel = conteudo.escolher(hier, sel, nome, valores));
  $: if (sel)
    gravarInputs(inputs_store, {
      areas: paraInput(sel.areas, opc.areas),
      disciplinas: paraInput(sel.disciplinas, opc.disciplinas),
      eixos: paraInput(sel.eixos, opc.eixos)
    });

  // As tabelas mostram o nível escolhido e, ao lado, o nível de cima: o eixo de cada item ou o item de cada subitem.
  $: porSubitem = `${inputs.nivel ?? ''}` === 'subitem';
  $: nivelTitulo = porSubitem ? 'Subitem' : 'Item';
  $: acimaTitulo = porSubitem ? 'Item' : 'Eixo';
</script>

Quatro jeitos de olhar o histórico de cada conteúdo desde o Vestibular 2016, além do volume: **regularidade** (cai em quase toda
prova?), **tendência** (está caindo mais ou menos nos últimos anos?) e **atraso** (sumiu há mais tempo que o normal?).
São indicadores do passado, não previsões.

<AnoVestibular />

```sql hierarquia
select distinct area, disciplina, eixo from uerj.recorrencia
```

<div class="filtros">
  <Filtro titulo="Área" opcoes={opc.areas ?? []} selecionados={sel?.areas ?? []} on:change={(e) => escolher('areas', e.detail)} />
  <span class="passo" aria-hidden="true">›</span>
  <Filtro titulo="Disciplina" opcoes={opc.disciplinas ?? []} selecionados={sel?.disciplinas ?? []} on:change={(e) => escolher('disciplinas', e.detail)} />
  <span class="passo" aria-hidden="true">›</span>
  <Filtro titulo="Eixo" opcoes={opc.eixos ?? []} selecionados={sel?.eixos ?? []} on:change={(e) => escolher('eixos', e.detail)} />
  <ButtonGroup name=nivel title="Ver por" color="#0072CE">
    <ButtonGroupItem valueLabel="Item" value="item" default />
    <ButtonGroupItem valueLabel="Subitem" value="subitem" />
  </ButtonGroup>
</div>

```sql base
select *, case when nivel = 'subitem' then item else eixo end as acima
from uerj.recorrencia
where nivel = '${inputs.nivel}'
    and area in ${inputs.areas.value}
    and disciplina in ${inputs.disciplinas.value}
    and eixo in ${inputs.eixos.value}
```

## Os mais regulares

Conteúdos que caíram na maior parte dos exames em que estavam no edital (no mínimo 5 exames).

```sql regulares
select
    rotulo,
    acima,
    regularidade,
    cast(qtd_exames as integer) || ' de ' || cast(greatest(exames_no_edital, qtd_exames) as integer) as caiu_em,
    qtd_questoes
from ${base}
where exames_no_edital >= 5
order by regularidade desc, qtd_questoes desc
```

<DataTable data={regulares} rows=15 search=true emptySet=pass emptyMessage="Nenhum conteúdo para esta seleção.">
  <Column id=rotulo title={nivelTitulo} wrap=true />
  <Column id=acima title={acimaTitulo} wrap=true />
  <Column id=caiu_em title="Caiu em (exames)" align=right />
  <Column id=regularidade title="Regularidade" fmt=pct0 contentType=bar barColor="#9cc8f0" />
  <Column id=qtd_questoes title="Questões desde 2016" />
</DataTable>

## Em alta e em baixa

Compara as questões por exame nos 6 exames mais recentes (vestibulares 2025 a 2027) com os exames anteriores, contando
só os exames em que o conteúdo estava no edital.

```sql variacao
select
    rotulo,
    acima,
    tendencia,
    replace(printf('%.1f', taxa_anterior), '.', ',') as antes,
    replace(printf('%.1f', taxa_recente), '.', ',') as recente,
    taxa_recente - taxa_anterior as variacao,
    case when taxa_recente >= taxa_anterior then '▲ +' else '▼ ' end || replace(printf('%.1f', taxa_recente - taxa_anterior), '.', ',') as variacao_txt,
    qtd_anterior,
    qtd_recente
from ${base}
where tendencia in ('em alta', 'em baixa')
```

```sql em_alta
select * from ${variacao} where tendencia = 'em alta' order by variacao desc
```

```sql em_baixa
select * from ${variacao} where tendencia = 'em baixa' order by variacao
```

<Grid cols=2>
<div>

### Em alta

<DataTable data={em_alta} rows=10 emptySet=pass emptyMessage="Nada em alta nesta seleção.">
  <Column id=rotulo title={nivelTitulo} wrap=true />
  <Column id=acima title={acimaTitulo} wrap=true />
  <Column id=antes title="Antes" align=right />
  <Column id=recente title="2025–27" align=right />
  <Column id=variacao_txt title="Variação" align=right />
</DataTable>

</div>
<div>

### Em baixa

<DataTable data={em_baixa} rows=10 emptySet=pass emptyMessage="Nada em baixa nesta seleção.">
  <Column id=rotulo title={nivelTitulo} wrap=true />
  <Column id=acima title={acimaTitulo} wrap=true />
  <Column id=antes title="Antes" align=right />
  <Column id=recente title="2025–27" align=right />
  <Column id=variacao_txt title="Variação" align=right />
</DataTable>

</div>
</Grid>

*Antes* e *2025–27* (vestibulares 2025 a 2027) são questões por exame. "Em alta": pelo menos 2 questões recentes e uma taxa 50% maior que a
anterior. "Em baixa": pelo menos 3 questões antes e uma taxa que caiu à metade ou menos.

## Sumidos que costumam voltar

Conteúdos do edital vigente que caíram em 3 exames ou mais, de tempos em tempos, e estão há pelo menos uma vez e meia o
intervalo normal sem cair. O **atraso** compara o tempo sem cair com esse intervalo: 2,0 significa o dobro do normal.

```sql sumidos
select
    rotulo,
    acima,
    qtd_exames,
    ultimo_exame,
    exames_desde_ultimo,
    replace(printf('%.1f', intervalo_medio), '.', ',') as intervalo,
    replace(printf('%.1f', indice_atraso), '.', ',') as atraso,
    indice_atraso
from ${base}
where sumido_que_volta
order by indice_atraso desc
```

<DataTable data={sumidos} rows=15 search=true emptySet=pass emptyMessage="Nenhum conteúdo sumido nesta seleção.">
  <Column id=rotulo title={nivelTitulo} wrap=true />
  <Column id=acima title={acimaTitulo} wrap=true />
  <Column id=qtd_exames title="Exames em que caiu" />
  <Column id=ultimo_exame title="Última vez" />
  <Column id=exames_desde_ultimo title="Exames sem cair" />
  <Column id=intervalo title="Intervalo normal (exames)" align=right />
  <Column id=atraso title="Atraso" align=right />
</DataTable>

<Alert status="info">
Um conteúdo "sumido" não tem mais chance de cair por estar sumido: a banca não segue uma fila. A lista serve para não
deixar de revisar o que já caiu algumas vezes e anda esquecido.
</Alert>

<style>
  .passo { color: hsl(var(--twc-primary)); font-size: 1.2rem; align-self: center; }
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.5rem; align-items: center; margin: 0.5rem 0 1rem; }
  .filtros :global(p) { margin: 0; }
</style>
