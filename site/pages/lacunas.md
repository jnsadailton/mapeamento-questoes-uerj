---
title: Lacunas
description: O que está no edital mais recente (2027) e nunca caiu desde 2016, e o que está há mais tempo sem cair.
sidebar_position: 7
---

<script>
  import { AREAS, gravarInputs, linhasDe, naOrdem, paraInput, unicas } from '$lib/filtros.js';

  $: opcAreas = unicas(linhasDe(areas), 'area', 'area', naOrdem(AREAS));
  let selAreas = null;
  $: if (!selAreas && opcAreas.length) selAreas = opcAreas.map((o) => o.valor);
  $: if (selAreas) gravarInputs(inputs_store, { areas: paraInput(selAreas, opcAreas) });
  $: ex = linhasDe(exemplo)[0];
  $: ult = linhasDe(ultimo_vestibular)[0];
</script>

Uma **lacuna** é um conteúdo que **está no edital mais recente**, o do Vestibular 2027, mas **nunca caiu**: nenhuma
questão foi classificada nele desde o Vestibular 2016, segundo os gabaritos comentados oficiais da UERJ.

```sql ultimo_vestibular
select
    ano,
    string_agg(strftime(data_aplicacao, '%d/%m/%Y'), ' e ' order by data_aplicacao) as datas
from uerj.exames
where ano = (select max(ano) from uerj.exames)
group by ano
```

<AnoVestibular />

{#if ult}
<Alert status="warning">
<b>As provas objetivas do Vestibular {ult.ano} já foram aplicadas</b> ({ult.datas}). Então esta página não é uma
previsão do que vai cair: ela mostra o que está no edital mais atual e não caiu em nenhuma prova desde 2016, inclusive
nas de {ult.ano}. Quando sair o próximo edital, a lista passa a usá-lo. Até lá, serve de referência, porque o programa
muda pouco de um ano para o outro (de 2026 para 2027, 251 dos 259 subitens se mantiveram).
</Alert>
{/if}

```sql exemplo
select area, item, subitem, qtd_exames_no_edital, primeiro_ano_no_edital
from uerj.lacunas
where nunca_caiu and area in ${inputs.areas.value}
order by qtd_exames_no_edital desc, area, item, subitem
limit 1
```

{#if ex}
<p class="exemplo">
  <b>Exemplo:</b> o subitem "{ex.subitem}", do item {ex.item} ({ex.area}), está no edital desde {ex.primeiro_ano_no_edital},
  em {ex.qtd_exames_no_edital} exames, e nenhuma questão foi classificada nele.
</p>
{/if}

<div class="tipos">
  <div class="tipo">
    <p class="tipo-nome">Lacuna antiga</p>
    <p>Está no edital desde antes do Vestibular 2021 e nunca caiu. A UERJ teve várias chances de cobrar e não cobrou.</p>
  </div>
  <div class="tipo">
    <p class="tipo-nome">Lacuna recente</p>
    <p>Entrou no edital no Vestibular 2021 ou depois. Teve poucas chances de cair, então ainda não diz muito.</p>
  </div>
  <div class="tipo">
    <p class="tipo-nome">Sumido</p>
    <p>Não é lacuna: já caiu, mas está há anos sem aparecer. Fica na segunda parte desta página.</p>
  </div>
</div>

<Alert status="info">
<b>Lacuna não quer dizer que nunca vai cair.</b> Se o conteúdo continuar no próximo edital, pode ser cobrado. As
lacunas mostram o que a UERJ costuma deixar de lado: com pouco tempo, comece pelo que cai sempre (veja "O que mais cai") sem ignorar estes
conteúdos. E "nunca caiu" se refere à classificação oficial: uma questão pode usar a ideia (conjuntos numa questão de
probabilidade, por exemplo) e ser classificada em outro item.
</Alert>

```sql areas
select distinct area from uerj.conteudo order by area
```

<Filtro titulo="Área" opcoes={opcAreas} selecionados={selAreas ?? []} on:change={(e) => (selAreas = e.detail)} />

```sql resumo
select
    count(*) as subitens,
    count(*) filter (where nunca_caiu) as lacunas,
    count(*) filter (where nunca_caiu and primeiro_ano_no_edital < 2021) as lacunas_antigas,
    count(*) filter (where nunca_caiu and primeiro_ano_no_edital >= 2021) as lacunas_recentes
from uerj.lacunas
where area in ${inputs.areas.value}
```

<Grid cols=4>
  <BigValue data={resumo} value=subitens title="Subitens no edital mais recente" emptySet=pass valueClass="valor" />
  <BigValue data={resumo} value=lacunas title="Lacunas (nunca caíram)" emptySet=pass valueClass="valor" />
  <BigValue data={resumo} value=lacunas_antigas title="Lacunas antigas" emptySet=pass valueClass="valor" />
  <BigValue data={resumo} value=lacunas_recentes title="Lacunas recentes" emptySet=pass valueClass="valor" />
</Grid>

## Subitens que nunca caíram

Dos que estão há mais tempo no edital para os mais novos.

```sql nunca
select
    subitem,
    item,
    case when primeiro_ano_no_edital < 2021 then 'antiga' else 'recente' end as tipo,
    primeiro_ano_no_edital,
    qtd_exames_no_edital
from uerj.lacunas
where nunca_caiu and area in ${inputs.areas.value}
order by qtd_exames_no_edital desc, item, subitem
```

<DataTable data={nunca} rows=20 search=true emptySet=pass emptyMessage="Nenhuma lacuna nesta seleção.">
  <Column id=subitem title="Subitem" wrap=true />
  <Column id=item title="Item" wrap=true />
  <Column id=tipo title="Lacuna" />
  <Column id=primeiro_ano_no_edital title="No edital desde o vestibular" fmt="0" />
  <Column id=qtd_exames_no_edital title="Exames no edital" />
</DataTable>

*Exames no edital*: em quantos dos 21 exames desde o Vestibular 2016 o subitem constava do conteúdo programático.

## Há mais tempo sem cair

Estes já caíram, mas não aparecem há anos. Para ver quais costumam voltar depois de um tempo, veja "Sumidos que
costumam voltar" na página Tendências.

```sql sem_cair
select subitem, item, qtd_questoes, ultimo_ano, anos_sem_cair
from uerj.lacunas
where not nunca_caiu and area in ${inputs.areas.value}
order by anos_sem_cair desc, qtd_questoes
limit 30
```

<DataTable data={sem_cair} rows=15 search=true emptySet=pass emptyMessage="Nada nesta seleção.">
  <Column id=subitem title="Subitem" wrap=true />
  <Column id=item title="Item" wrap=true />
  <Column id=qtd_questoes title="Questões desde 2016" />
  <Column id=ultimo_ano title="Último vestibular" fmt="0" />
  <Column id=anos_sem_cair title="Anos sem cair" />
</DataTable>

<style>
  .exemplo { max-width: 72ch; padding: 0.6rem 0.8rem; border-left: 3px solid hsl(var(--twc-accent));
             background: hsl(var(--twc-accent) / 0.08); font-size: 0.95rem; }
  .tipos { display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 0.75rem 1.5rem; margin: 1rem 0; }
  .tipo { border-top: 2px solid hsl(var(--twc-base-heading)); padding-top: 0.5rem; }
  .tipo p { margin: 0; font-size: 0.9rem; line-height: 1.5; }
  .tipo .tipo-nome { margin-bottom: 0.25rem; font-family: var(--fonte-titulo); font-size: 1.2rem; font-weight: 600;
                     color: hsl(var(--twc-base-heading)); }
</style>
