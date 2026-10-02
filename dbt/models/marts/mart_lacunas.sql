-- Subitens do edital vigente com o histórico de cobrança: quantas vezes caíram e quando foi a última.
-- `nunca_caiu` marca as lacunas: estão no edital mais recente e nenhuma questão desde 2016 foi ligada a eles.
with cobranca as (
    select id_conteudo, sum(qtd_questoes) as qtd_questoes, max(ano) as ultimo_ano, count(distinct id_exame) as qtd_exames
    from {{ ref('mart_incidencia') }}
    where nivel = 'subitem'
    group by id_conteudo
),

ultimo_exame as (
    select max(ano) as ano from {{ ref('dim_exame') }}
)

select
    d.id_conteudo as id_subitem,
    d.id_area,
    d.disciplina,
    d.eixo,
    d.item,
    d.subitem,
    coalesce(c.qtd_questoes, 0) as qtd_questoes,
    coalesce(c.qtd_exames, 0) as qtd_exames,
    c.ultimo_ano,
    (select ano from ultimo_exame) - c.ultimo_ano as anos_sem_cair,
    c.id_conteudo is null as nunca_caiu
from {{ ref('dim_conteudo') }} as d
left join cobranca as c using (id_conteudo)
where d.nivel = 'subitem' and d.vigente
