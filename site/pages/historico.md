---
title: Histórico por conteúdo
description: A série histórica de cada eixo, item e subitem do programa, de 2016 a 2027.
sidebar_position: 4
---

Escolha uma área e um eixo para ver em que exames cada item caiu; depois escolha um item para descer até os subitens e
as questões. Cada célula mostra quantas questões do exame tocaram o conteúdo (vazia quando nenhuma).

```sql areas
select distinct area from uerj.conteudo order by area
```

```sql eixos
select distinct id_eixo, eixo from uerj.conteudo where area = '${inputs.area.value}' order by id_eixo
```

<Grid cols=2>
  <Dropdown data={areas} name=area value=area title="Área" defaultValue="Matemática" />
  <Dropdown data={eixos} name=eixo value=id_eixo label=eixo title="Eixo" />
</Grid>

## Itens do eixo, exame a exame

```sql mapa_itens
select
    e.rotulo as exame,
    e.id_exame,
    c.item || case when c.vigente then '' else ' *' end as item,
    c.id_item,
    i.qtd_questoes as questoes
from uerj.exames as e
cross join (
    select id_item, item, vigente from uerj.conteudo where id_eixo = '${inputs.eixo.value}' and nivel = 'item'
) as c
left join uerj.incidencia as i
    on i.id_exame = e.id_exame and i.nivel = 'item' and i.id_conteudo = c.id_item
```

<Heatmap
  data={mapa_itens}
  x=exame
  xSort=id_exame
  y=item
  ySort=id_item
  value=questoes
  xLabelRotation=-45
  legend=false
  cellHeight=32
  nullsZero=false
  min=0
  rightPadding=40
  emptySet=pass
  emptyMessage="Nenhum conteúdo para mostrar."
/>

Itens marcados com * não estão mais no edital de 2027; eles aparecem porque caíram em exames anteriores.

## Um item em detalhe

```sql itens_eixo
select id_item, item || ' (' || questoes || ')' as rotulo, questoes
from (
    select c.id_item, c.item, cast(coalesce(sum(i.qtd_questoes), 0) as integer) as questoes
    from uerj.conteudo as c
    left join uerj.incidencia as i on i.nivel = 'item' and i.id_conteudo = c.id_item
    where c.id_eixo = '${inputs.eixo.value}' and c.nivel = 'item'
    group by c.id_item, c.item
)
order by questoes desc, item
```

{#if itens_eixo.length}
<Dropdown data={itens_eixo} name=item value=id_item label=rotulo order="questoes desc" defaultValue={itens_eixo[0].id_item} title="Item (questões desde 2016)" />
{/if}

```sql resumo_item
select
    coalesce(sum(qtd_questoes), 0) as questoes,
    count(distinct id_exame) as exames,
    max(ano) as ultimo_ano
from uerj.incidencia
where nivel = 'item' and id_conteudo = '${inputs.item.value}'
```

<Grid cols=3>
  <BigValue data={resumo_item} value=questoes title="Questões desde 2016" emptySet=pass emptyMessage="—" />
  <BigValue data={resumo_item} value=exames title="Exames em que caiu (de 21)" emptySet=pass emptyMessage="—" />
  <BigValue data={resumo_item} value=ultimo_ano fmt="0" title="Último vestibular em que caiu" emptySet=pass emptyMessage="—" />
</Grid>

```sql mapa_subitens
select
    e.rotulo as exame,
    e.id_exame,
    c.subitem || case when c.vigente then '' else ' *' end as subitem,
    c.id_subitem,
    i.qtd_questoes as questoes
from uerj.exames as e
cross join (
    select id_subitem, subitem, vigente from uerj.conteudo
    where id_item = '${inputs.item.value}' and nivel = 'subitem'
) as c
left join uerj.incidencia as i
    on i.id_exame = e.id_exame and i.nivel = 'subitem' and i.id_conteudo = c.id_subitem
```

<Heatmap
  data={mapa_subitens}
  x=exame
  xSort=id_exame
  y=subitem
  ySort=id_subitem
  value=questoes
  xLabelRotation=-45
  legend=false
  cellHeight=32
  nullsZero=false
  min=0
  rightPadding=40
  emptySet=pass
  emptyMessage="Nenhum conteúdo para mostrar."
/>

Quando o comentário oficial só informa o item, a questão conta para o item, mas não para nenhum subitem.

```sql questoes_item
select
    q.id_questao,
    q.classificacao,
    q.resposta,
    q.percentual_acertos / 100 as acertos,
    q.observacoes,
    q.url_comentario
from uerj.questoes as q
where q.id_questao in (select id_questao from uerj.classificacoes where id_item = '${inputs.item.value}')
order by q.id_questao desc
```

<DataTable data={questoes_item} rows=15 search=true emptySet=pass emptyMessage="Nenhuma questão ligada a este item.">
  <Column id=id_questao title="Questão" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=resposta title="Gabarito" />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=observacoes title="Adendo do projeto" wrap=true />
  <Column id=url_comentario title="Comentário" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>
