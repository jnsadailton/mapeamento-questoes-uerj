-- Hierarquia canônica de conteúdo (Área › Eixo › Item › Subitem), uma linha por item e uma por subitem.
-- IDs: AREA.E.II.SS (ex.: MAT.2.03.01). A base é o edital de 2027; itens e subitens de editais anteriores que
-- não existem mais ficam com `vigente = false`.
with base as (
    select
        *,
        split_part(id_subitem, '.', 1) || '.' || split_part(id_subitem, '.', 2) as id_eixo,
        split_part(id_subitem, '.', 1) || '.' || split_part(id_subitem, '.', 2) || '.'
            || split_part(id_subitem, '.', 3) as id_item
    from {{ ref('conteudo_base') }}
),

itens as (
    select distinct
        id_item as id_conteudo,
        'item' as nivel,
        area_sigla as id_area, area, disciplina, id_eixo, eixo, id_item, item,
        null as id_subitem, null as subitem,
        item_vigente as vigente
    from base
),

subitens as (
    select
        id_subitem as id_conteudo,
        'subitem' as nivel,
        area_sigla as id_area, area, disciplina, id_eixo, eixo, id_item, item,
        id_subitem, subitem,
        subitem_vigente as vigente
    from base
)

select * from itens
union all
select * from subitens
