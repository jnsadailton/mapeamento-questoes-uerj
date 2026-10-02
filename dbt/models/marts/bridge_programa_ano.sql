-- Em que exames (e anos) cada subitem canônico consta do edital.
select distinct
    p.id_exame,
    cast(split_part(p.id_exame, '-', 1) as integer) as ano,
    p.id_conteudo as id_subitem
from {{ ref('int_programa_ligado') }} as p
where p.id_conteudo is not null
