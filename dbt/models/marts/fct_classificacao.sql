-- Questão × conteúdo (N:N). Uma linha por conteúdo ligado a cada versão de questão: subitem, ou só o item quando o
-- comentário não permite chegar ao subitem. Disciplina: a do item na hierarquia, exceto no bloco de língua
-- estrangeira, em que é "Língua Estrangeira".
with ligadas as (
    select * from {{ ref('int_classificacao_ligada') }}
    where id_conteudo is not null
)

select
    l.id_questao,
    l.id_exame,
    l.numero,
    l.idioma,
    l.id_conteudo,
    c.nivel as nivel_conteudo,
    c.id_area,
    c.id_eixo,
    c.id_item,
    c.id_subitem,
    case when l.idioma is not null then 'Língua Estrangeira' else c.disciplina end as disciplina,
    min(l.ordem) as ordem,
    string_agg(distinct l.origem, ', ' order by l.origem) as origem,
    bool_or(l.eixo_atribuido) as eixo_atribuido,
    string_agg(distinct l.observacao, ' ' order by l.observacao) as observacao,
    string_agg(
        distinct l.item || coalesce(' › ' || nullif(trim(l.parte_subitem), ''), ''), ' | '
        order by l.item || coalesce(' › ' || nullif(trim(l.parte_subitem), ''), '')
    ) as texto_no_comentario
from ligadas as l
inner join {{ ref('dim_conteudo') }} as c on c.id_conteudo = l.id_conteudo
group by all
