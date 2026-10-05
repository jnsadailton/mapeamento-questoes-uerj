-- Questão × conteúdo, com os nomes da hierarquia (Área › Eixo › Item › Subitem).
select
    c.id_questao,
    c.id_exame,
    e.ano,
    e.nome as exame,
    c.numero,
    c.idioma,
    d.area,
    c.disciplina,
    d.id_eixo,
    d.eixo,
    d.id_item,
    d.item,
    d.id_subitem,
    d.subitem,
    c.nivel_conteudo,
    d.vigente,
    c.origem,
    c.eixo_atribuido,
    c.observacao,
    q.percentual_acertos,
    q.anulada
from fct_classificacao as c
inner join dim_conteudo as d using (id_conteudo)
inner join dim_exame as e using (id_exame)
inner join fct_questao as q using (id_questao)
order by c.id_questao, d.id_item, d.id_subitem nulls first
