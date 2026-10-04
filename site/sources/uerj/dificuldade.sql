-- Percentual de acertos por item e subitem.
select
    m.nivel,
    m.id_conteudo,
    d.area,
    m.disciplina,
    d.id_eixo,
    d.eixo,
    d.id_item,
    d.item,
    d.id_subitem,
    d.subitem,
    m.rotulo,
    m.qtd_questoes,
    m.media_acertos,
    m.mediana_acertos,
    m.min_acertos,
    m.max_acertos
from mart_dificuldade as m
inner join dim_conteudo as d using (id_conteudo)
