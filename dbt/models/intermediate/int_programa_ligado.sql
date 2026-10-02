-- Subitens do edital de cada exame ligados à hierarquia canônica pelo dicionário.
select
    c.id_exame,
    c.area_no_edital,
    c.eixo,
    c.item,
    c.subitem,
    {{ normalizar_texto('c.item') }} as chave_item,
    {{ normalizar_texto('c.subitem') }} as chave_subitem,
    d.id_conteudo
from {{ ref('stg_conteudo_programatico') }} as c
left join (select distinct chave_item, chave_subitem, id_conteudo from {{ ref('int_dicionario') }}) as d
    on d.chave_item = {{ normalizar_texto('c.item') }}
    and d.chave_subitem = {{ normalizar_texto('c.subitem') }}
