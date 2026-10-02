-- Percentual de acertos por conteúdo (item e subitem). Cada versão de questão com percentual publicado é um ponto;
-- ficam de fora as anuladas e as questões sem percentual (2021, 2024-2, 2027-2 e as de nível estimado).
with pontos as (
    select c.id_item, c.id_subitem, q.id_questao, q.percentual_acertos
    from {{ ref('fct_classificacao') }} as c
    inner join {{ ref('fct_questao') }} as q using (id_questao)
    where q.percentual_acertos is not null and not q.anulada
),

niveis as (
    select 'item' as nivel, id_item as id_conteudo, id_questao, percentual_acertos from pontos
    union all
    select 'subitem', id_subitem, id_questao, percentual_acertos from pontos where id_subitem is not null
)

select
    n.nivel,
    n.id_conteudo,
    d.id_area,
    d.disciplina,
    coalesce(d.subitem, d.item) as rotulo,
    count(distinct n.id_questao) as qtd_questoes,
    round(avg(n.percentual_acertos), 2) as media_acertos,
    round(median(n.percentual_acertos), 2) as mediana_acertos,
    min(n.percentual_acertos) as min_acertos,
    max(n.percentual_acertos) as max_acertos
from (select distinct * from niveis) as n
inner join {{ ref('dim_conteudo') }} as d using (id_conteudo)
group by all
