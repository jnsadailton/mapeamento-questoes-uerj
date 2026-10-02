-- Um comentário pode citar vários subitens no mesmo campo, separados por ";". Cada parte é ligada à hierarquia
-- separadamente, pela chave normalizada (item, parte do subitem).
with partes as (
    select
        *,
        unnest(string_split(coalesce(subitem, ''), ';')) as parte_subitem
    from {{ ref('int_classificacao_curada') }}
)

select
    *,
    {{ normalizar_texto('item') }} as chave_item,
    {{ normalizar_texto('parte_subitem') }} as chave_subitem
from partes
where trim(parte_subitem) <> '' or coalesce(subitem, '') = ''
