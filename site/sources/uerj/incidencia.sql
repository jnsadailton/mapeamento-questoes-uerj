-- Questões por exame e conteúdo nos quatro níveis da hierarquia. A unidade é o número da questão: as versões de
-- língua estrangeira contam uma vez (regra documentada em mart_incidencia).
with areas as (
    select distinct id_area, area from dim_conteudo
),

eixos as (
    select distinct id_eixo, eixo from dim_conteudo
)

select
    i.id_exame,
    e.nome as exame,
    case when e.tipo = 'Único' then e.ano || ' · EU' else e.ano || ' · ' || e.numero || 'º EQ' end as rotulo_exame,
    i.ano,
    i.tipo_exame,
    i.nivel,
    i.id_conteudo,
    i.rotulo,
    a.area,
    coalesce(d.disciplina, '') as disciplina,
    coalesce(d.id_eixo, x.id_eixo) as id_eixo,
    coalesce(d.eixo, x.eixo) as eixo,
    d.id_item,
    d.item,
    d.subitem,
    i.qtd_questoes,
    i.proporcao_do_exame
from mart_incidencia as i
inner join dim_exame as e using (id_exame)
inner join areas as a using (id_area)
left join dim_conteudo as d on d.id_conteudo = i.id_conteudo
left join eixos as x on x.id_eixo = i.id_conteudo
