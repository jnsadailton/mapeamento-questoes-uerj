---
title: Lacunas
description: O que está no edital de 2027 e nunca caiu desde 2016, e o que está há mais tempo sem cair.
sidebar_position: 7
---

<script>
  import { AREAS, gravarInputs, linhasDe, naOrdem, paraInput, unicas } from '$lib/filtros.js';

  $: opcAreas = unicas(linhasDe(areas), 'area', 'area', naOrdem(AREAS));
  let selAreas = null;
  $: if (!selAreas && opcAreas.length) selAreas = opcAreas.map((o) => o.valor);
  $: if (selAreas) gravarInputs(inputs_store, { areas: paraInput(selAreas, opcAreas) });
</script>

Uma **lacuna** é um subitem do edital vigente (2027) que nenhuma questão tocou desde 2016. As redações antigas de
editais e comentários foram ligadas ao subitem atual equivalente, então uma questão classificada com a redação de 2016
conta para o subitem de hoje.

```sql areas
select distinct area from uerj.conteudo order by area
```

<Filtro titulo="Área" opcoes={opcAreas} selecionados={selAreas ?? []} on:change={(e) => (selAreas = e.detail)} />

```sql resumo
select
    count(*) as subitens,
    count(*) filter (where nunca_caiu) as lacunas,
    count(*) filter (where nunca_caiu and primeiro_ano_no_edital >= 2021) as lacunas_recentes,
    count(*) filter (where nunca_caiu and qtd_exames_no_edital = 21) as lacunas_desde_2016
from uerj.lacunas
where area in ${inputs.areas.value}
```

<Grid cols=3>
  <BigValue data={resumo} value=lacunas title="Subitens que nunca caíram" emptySet=pass valueClass="valor" />
  <BigValue data={resumo} value=lacunas_desde_2016 title="No edital em todos os 21 exames" emptySet=pass valueClass="valor" />
  <BigValue data={resumo} value=lacunas_recentes title="Entraram no edital em 2021 ou depois" emptySet=pass valueClass="valor" />
</Grid>

<Alert status="info">
Nem toda lacuna pesa igual. Um subitem que entrou no edital em 2024 teve poucas chances de cair; um que está lá desde
2016 e nunca caiu diz mais. Por isso a tabela mostra desde quando cada subitem está no edital e em quantos exames ele
constou.
</Alert>

## Subitens que nunca caíram

```sql nunca
select area, eixo, item, subitem, primeiro_ano_no_edital, qtd_exames_no_edital
from uerj.lacunas
where nunca_caiu and area in ${inputs.areas.value}
order by qtd_exames_no_edital desc, area, eixo, item, subitem
```

<DataTable data={nunca} rows=25 search=true emptySet=pass emptyMessage="Nenhuma lacuna nesta seleção.">
  <Column id=area title="Área" />
  <Column id=eixo title="Eixo" wrap=true />
  <Column id=item title="Item" wrap=true />
  <Column id=subitem title="Subitem" wrap=true />
  <Column id=primeiro_ano_no_edital title="No edital desde" fmt="0" />
  <Column id=qtd_exames_no_edital title="Exames com o subitem no edital" />
</DataTable>

## Há mais tempo sem cair

Subitens que já caíram, ordenados pelo tempo desde a última cobrança.

```sql sem_cair
select eixo, item, subitem, qtd_questoes, qtd_exames, ultimo_ano, anos_sem_cair
from uerj.lacunas
where not nunca_caiu and area in ${inputs.areas.value}
order by anos_sem_cair desc, qtd_questoes
limit 30
```

<DataTable data={sem_cair} rows=15 search=true emptySet=pass emptyMessage="Nada nesta seleção.">
  <Column id=eixo title="Eixo" wrap=true />
  <Column id=item title="Item" wrap=true />
  <Column id=subitem title="Subitem" wrap=true />
  <Column id=qtd_questoes title="Questões desde 2016" />
  <Column id=ultimo_ano title="Último vestibular" fmt="0" />
  <Column id=anos_sem_cair title="Anos sem cair" />
</DataTable>

O ano é o do vestibular, não o da aplicação: o vestibular 2027 teve as provas aplicadas em 2026.
