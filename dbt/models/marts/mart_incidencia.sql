-- Quantas questões de cada exame tocaram cada conteúdo, nos quatro níveis da hierarquia (área, eixo, item, subitem).
--
-- Regra de contagem: a unidade é o NÚMERO da questão no exame (60 por exame). No bloco de língua estrangeira as três
-- versões (ES, FR, EN) ocupam o mesmo número; o conteúdo conta uma vez se aparecer em qualquer uma delas. Uma questão
-- com várias classificações conta uma vez para cada conteúdo. Questões anuladas entram (o conteúdo foi cobrado).
with base as (
    select id_exame, numero, id_area, id_eixo, id_item, id_subitem
    from {{ ref('fct_classificacao') }}
),

niveis as (
    select id_exame, numero, 'area' as nivel, id_area as id_conteudo from base
    union all
    select id_exame, numero, 'eixo', id_eixo from base
    union all
    select id_exame, numero, 'item', id_item from base
    union all
    select id_exame, numero, 'subitem', id_subitem from base where id_subitem is not null
),

rotulos as (
    select distinct id_area as id_conteudo, id_area, area as rotulo from {{ ref('dim_conteudo') }}
    union all
    select distinct id_eixo, id_area, eixo from {{ ref('dim_conteudo') }}
    union all
    select id_conteudo, id_area, coalesce(subitem, item) from {{ ref('dim_conteudo') }}
)

select
    n.id_exame,
    e.ano,
    e.tipo as tipo_exame,
    n.nivel,
    n.id_conteudo,
    r.id_area,
    r.rotulo,
    count(distinct n.numero) as qtd_questoes,
    round(count(distinct n.numero) / 60.0, 4) as proporcao_do_exame
from niveis as n
inner join {{ ref('dim_exame') }} as e using (id_exame)
inner join rotulos as r using (id_conteudo)
group by all
